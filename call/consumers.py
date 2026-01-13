import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Send message to room group
        # We expect messages to have a 'type' key that matches a method name
        # e.g., 'call_offer', 'call_answer', 'new_ice_candidate'
        # But here we just broadcast everything to the other peer(s)
        
        event_type = text_data_json.get('type')
        if event_type == 'call_offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_offer',
                    'offer': text_data_json['offer']
                }
            )
        elif event_type == 'call_answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_answer',
                    'answer': text_data_json['answer']
                }
            )
        elif event_type == 'new_ice_candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_ice_candidate',
                    'candidate': text_data_json['candidate']
                }
            )

    # Receive message from room group
    async def call_offer(self, event):
        # Send offer to WebSocket
        # Don't send back to sender ideally, but for simplicity we filter on client side or simple broadcast
        # In a real app we might exclude the sender
        if self.channel_name != event.get('sender_channel_name'): # We need to pass sender_channel_name if we want to filter
             await self.send(text_data=json.dumps({
                'type': 'call_offer',
                'offer': event['offer']
            }))
             
    # Redefining receive/send logic to simple broadcast for now, 
    # but strictly speaking, we need to handle the "don't echo back" logic.
    # Let's trust the client handles "ignoring own messages" or we implement source tracking.
    # Improved implementation below:

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal_message',
                'message': data,
                'sender_channel_name': self.channel_name
            }
        )

    async def signal_message(self, event):
        # Send message to WebSocket only if it's not from the sender
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=json.dumps(event['message']))
