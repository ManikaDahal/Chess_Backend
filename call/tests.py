from django.test import TestCase
from channels.testing import WebsocketCommunicator
from django_project.asgi import application
import json

class CallTests(TestCase):
    async def test_call_consumer(self):
        # Connect client 1
        communicator = WebsocketCommunicator(application, "/ws/call/testroom/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Connect client 2 (needs to be connected to receive broadcast)
        communicator2 = WebsocketCommunicator(application, "/ws/call/testroom/")
        connected2, subprotocol2 = await communicator2.connect()
        self.assertTrue(connected2)

        # Test sending an offer from client 1
        offer_data = {
            'type': 'call_offer',
            'offer': {'sdp': 'dummy_sdp', 'type': 'offer'}
        }
        await communicator.send_json_to(offer_data)

        # Client 2 should receive it
        response2 = await communicator2.receive_json_from()
        self.assertEqual(response2['type'], 'call_offer')
        self.assertEqual(response2['offer'], offer_data['offer'])

        # Client 1 should NOT receive it (based on our logic)
        self.assertTrue(await communicator.receive_nothing())

        # Disconnect
        await communicator.disconnect()
        await communicator2.disconnect()
