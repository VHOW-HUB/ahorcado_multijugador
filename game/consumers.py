import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Sala

class GameConsumer(AsyncWebsocketConsumer):
    # Diccionario para almacenar el estado de las salas en memoria
    salas_estado = {}
    
    async def connect(self):
        self.codigo_sala = self.scope['url_route']['kwargs']['codigo_sala']
        self.room_group_name = f'sala_{self.codigo_sala}'
        
        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Inicializar estado de la sala si no existe
        if self.codigo_sala not in self.salas_estado:
            self.salas_estado[self.codigo_sala] = {
                'jugadores': [],
                'juego_iniciado': False,
                'ronda_actual': 0,
                'jugador_adivinando': None,
                'palabra_secreta': '',
                'letras_adivinadas': [],
                'errores': 0,
                'puntos': {'jugador1': 0, 'jugador2': 0},
                'tiempo_restante': 90,
                'timer_activo': False,
                'timer_task': None,
                'desconectado': None,
                'tiempo_espera_reconexion': 20,
                'reconexion_task': None,
            }
        
        estado = self.salas_estado[self.codigo_sala]
        
        # Agregar jugador
        if len(estado['jugadores']) < 2:
            jugador_id = f'jugador{len(estado["jugadores"]) + 1}'
            estado['jugadores'].append({
                'id': jugador_id,
                'channel_name': self.channel_name
            })
            self.jugador_id = jugador_id
            
            # Notificar a todos los jugadores
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'jugador_conectado',
                    'jugador_id': jugador_id,
                    'total_jugadores': len(estado['jugadores'])
                }
            )
            
            # Si hay 2 jugadores, iniciar el juego
            if len(estado['jugadores']) == 2:
                await self.iniciar_juego()
        else:
            # Sala llena
            await self.send(text_data=json.dumps({
                'tipo': 'error',
                'mensaje': 'La sala está llena'
            }))
            await self.close()
    
    async def disconnect(self, close_code):
        estado = self.salas_estado.get(self.codigo_sala)
        
        if estado:
            # Marcar como desconectado
            estado['desconectado'] = self.jugador_id
            
            # Iniciar contador de reconexión
            if estado['reconexion_task']:
                estado['reconexion_task'].cancel()
            estado['reconexion_task'] = asyncio.create_task(self.iniciar_contador_reconexion())
            
            # Notificar desconexión
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'jugador_desconectado',
                    'jugador_id': self.jugador_id
                }
            )
        
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        tipo = data.get('tipo')
        
        if tipo == 'enviar_palabra':
            await self.procesar_palabra(data.get('palabra'))
        elif tipo == 'adivinar_letra':
            await self.procesar_letra(data.get('letra'))
        elif tipo == 'reconectado':
            await self.procesar_reconexion()
    
    async def iniciar_juego(self):
        estado = self.salas_estado[self.codigo_sala]
        estado['juego_iniciado'] = True
        estado['ronda_actual'] = 1
        
        # Seleccionar aleatoriamente quién adivina primero
        estado['jugador_adivinando'] = random.choice(['jugador1', 'jugador2'])
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'iniciar_ronda',
                'jugador_adivinando': estado['jugador_adivinando'],
                'ronda': estado['ronda_actual'],
                'puntos': estado['puntos']
            }
        )
    
    async def procesar_palabra(self, palabra):
        estado = self.salas_estado[self.codigo_sala]
        
        if not palabra or len(palabra) < 3:
            return
        
        estado['palabra_secreta'] = palabra.upper()
        estado['letras_adivinadas'] = []
        estado['errores'] = 0
        estado['tiempo_restante'] = 90
        estado['timer_activo'] = True
        
        # Iniciar el timer en el servidor
        if estado['timer_task']:
            estado['timer_task'].cancel()
        estado['timer_task'] = asyncio.create_task(self.ejecutar_timer())
        
        # Notificar que la ronda puede empezar
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'palabra_recibida',
                'longitud_palabra': len(palabra),
                'tiempo_restante': 90
            }
        )
    
    async def procesar_letra(self, letra):
        estado = self.salas_estado[self.codigo_sala]
        letra = letra.upper()
        
        if letra in estado['letras_adivinadas']:
            return
        
        estado['letras_adivinadas'].append(letra)
        
        # Verificar si la letra está en la palabra
        if letra in estado['palabra_secreta']:
            # Letra correcta
            palabra_revelada = ''.join(
                [l if l in estado['letras_adivinadas'] else '_' 
                 for l in estado['palabra_secreta']]
            )
            
            # Verificar si ganó
            if '_' not in palabra_revelada:
                await self.finalizar_ronda(ganador=estado['jugador_adivinando'])
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'letra_correcta',
                        'letra': letra,
                        'palabra_revelada': palabra_revelada,
                        'errores': estado['errores']
                    }
                )
        else:
            # Letra incorrecta
            estado['errores'] += 1
            
            # Verificar si perdió (8 errores)
            if estado['errores'] >= 8:
                # Pierde el que adivina, gana el otro
                jugador_ganador = 'jugador1' if estado['jugador_adivinando'] == 'jugador2' else 'jugador2'
                await self.finalizar_ronda(ganador=jugador_ganador)
            else:
                palabra_revelada = ''.join(
                    [l if l in estado['letras_adivinadas'] else '_' 
                     for l in estado['palabra_secreta']]
                )
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'letra_incorrecta',
                        'letra': letra,
                        'palabra_revelada': palabra_revelada,
                        'errores': estado['errores']
                    }
                )
    
    async def finalizar_ronda(self, ganador):
        estado = self.salas_estado[self.codigo_sala]
        estado['puntos'][ganador] += 1
        estado['timer_activo'] = False
        
        # Cancelar timer
        if estado['timer_task']:
            estado['timer_task'].cancel()
            estado['timer_task'] = None
        
        # Verificar si alguien llegó a 5 puntos
        if estado['puntos'][ganador] >= 5:
            await self.finalizar_juego(ganador)
        else:
            # Siguiente ronda con roles invertidos
            estado['ronda_actual'] += 1
            estado['jugador_adivinando'] = 'jugador1' if estado['jugador_adivinando'] == 'jugador2' else 'jugador2'
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ronda_terminada',
                    'ganador': ganador,
                    'palabra_secreta': estado['palabra_secreta'],
                    'puntos': estado['puntos'],
                    'siguiente_adivinando': estado['jugador_adivinando'],
                    'ronda': estado['ronda_actual']
                }
            )
    
    async def finalizar_juego(self, ganador):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'juego_terminado',
                'ganador': ganador,
                'puntos': self.salas_estado[self.codigo_sala]['puntos']
            }
        )
    
    async def procesar_reconexion(self):
        estado = self.salas_estado.get(self.codigo_sala)
        if estado and estado['desconectado'] == self.jugador_id:
            estado['desconectado'] = None
            
            # Cancelar tarea de reconexión
            if estado['reconexion_task']:
                estado['reconexion_task'].cancel()
                estado['reconexion_task'] = None
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'jugador_reconectado',
                    'jugador_id': self.jugador_id
                }
            )
    
    async def ejecutar_timer(self):
        """Ejecuta el contador de tiempo de la ronda"""
        estado = self.salas_estado.get(self.codigo_sala)
        if not estado:
            return
        
        try:
            while estado['tiempo_restante'] > 0 and estado['timer_activo']:
                await asyncio.sleep(1)
                estado['tiempo_restante'] -= 1
                
                # Enviar actualización cada 5 segundos o en los últimos 10
                if estado['tiempo_restante'] % 5 == 0 or estado['tiempo_restante'] <= 10:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'actualizar_timer',
                            'tiempo_restante': estado['tiempo_restante']
                        }
                    )
            
            # Si se acabó el tiempo, el jugador que adivina pierde
            if estado['tiempo_restante'] <= 0 and estado['timer_activo']:
                jugador_ganador = 'jugador1' if estado['jugador_adivinando'] == 'jugador2' else 'jugador2'
                await self.finalizar_ronda(ganador=jugador_ganador)
        except asyncio.CancelledError:
            # Timer cancelado, esto es normal
            pass
    
    async def iniciar_contador_reconexion(self):
        """Ejecuta el contador de reconexión"""
        estado = self.salas_estado.get(self.codigo_sala)
        if not estado:
            return
        
        try:
            tiempo_restante = 20
            while tiempo_restante > 0 and estado['desconectado']:
                await asyncio.sleep(1)
                tiempo_restante -= 1
            
            # Si después de 20 segundos sigue desconectado, el otro jugador gana
            if estado['desconectado'] and tiempo_restante <= 0:
                jugador_conectado = 'jugador1' if estado['desconectado'] == 'jugador2' else 'jugador2'
                estado['puntos'][jugador_conectado] = 5
                await self.finalizar_juego(ganador=jugador_conectado)
        except asyncio.CancelledError:
            # Reconexión cancelada, esto es normal
            pass
    
    # Handlers para enviar mensajes al WebSocket
    async def jugador_conectado(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'jugador_conectado',
            'jugador_id': event['jugador_id'],
            'total_jugadores': event['total_jugadores'],
            'tu_id': self.jugador_id
        }))
    
    async def iniciar_ronda(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'iniciar_ronda',
            'jugador_adivinando': event['jugador_adivinando'],
            'ronda': event['ronda'],
            'puntos': event['puntos'],
            'tu_id': self.jugador_id
        }))
    
    async def palabra_recibida(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'palabra_recibida',
            'longitud_palabra': event['longitud_palabra'],
            'tiempo_restante': event['tiempo_restante']
        }))
    
    async def letra_correcta(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'letra_correcta',
            'letra': event['letra'],
            'palabra_revelada': event['palabra_revelada'],
            'errores': event['errores']
        }))
    
    async def letra_incorrecta(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'letra_incorrecta',
            'letra': event['letra'],
            'palabra_revelada': event['palabra_revelada'],
            'errores': event['errores']
        }))
    
    async def ronda_terminada(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'ronda_terminada',
            'ganador': event['ganador'],
            'palabra_secreta': event['palabra_secreta'],
            'puntos': event['puntos'],
            'siguiente_adivinando': event['siguiente_adivinando'],
            'ronda': event['ronda']
        }))
    
    async def juego_terminado(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'juego_terminado',
            'ganador': event['ganador'],
            'puntos': event['puntos']
        }))
    
    async def jugador_desconectado(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'jugador_desconectado',
            'jugador_id': event['jugador_id']
        }))
    
    async def jugador_reconectado(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'jugador_reconectado',
            'jugador_id': event['jugador_id']
        }))
    
    async def actualizar_timer(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'actualizar_timer',
            'tiempo_restante': event['tiempo_restante']
        }))
