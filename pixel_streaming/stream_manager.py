import json
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

class PixelStreamEngine:
    def __init__(self):
        # STUN/TURN सर्वर्स: यह सुनिश्चित करेगा कि प्लेयर दुनिया के किसी भी कोने में हो, गेम लैग न करे
        self.ice_servers = [
            RTCIceServer(urls=["stun:stun.l.google.com:19302"])
        ]
        self.rtc_config = RTCConfiguration(iceServers=self.ice_servers)
        self.active_connections = {}

    async def create_stream_connection(self, player_id: str, offer_sdp: str, offer_type: str) -> dict:
        """
        फोन (ऐप) से WebRTC Offer लेगा और सर्वर से Video Stream का Answer देगा।
        """
        pc = RTCPeerConnection(configuration=self.rtc_config)
        self.active_connections[player_id] = pc

        # 1. डेटा चैनल (Data Channel) - फोन से जॉयस्टिक और बटन के इनपुट लेने के लिए (Zero Latency)
        @pc.on("datachannel")
        def on_datachannel(channel):
            print(f"[PIXEL STREAM]: Data channel '{channel.label}' established for {player_id}.")
            
            @channel.on("message")
            def on_message(message):
                # यहाँ फोन से आया प्लेयर का इनपुट (X, Y movement, Shoot) सीधा गेम इंजन को जाएगा
                self.process_player_input(player_id, message)

        # 2. वीडियो स्ट्रीमिंग (Video Track)
        # जब C++ या AI 3D गेम रेंडर करेगा, तो उसके फ्रेम्स (Frames) इस ट्रैक के ज़रिए फोन पर जाएंगे
        # pc.addTrack(GameVideoTrack()) # असली रेंडरिंग के समय यह एक्टिवेट होगा

        # फोन से आया कनेक्शन (Offer) सेट करना
        offer = RTCSessionDescription(sdp=offer_sdp, type=offer_type)
        await pc.setRemoteDescription(offer)

        # सर्वर से जवाब (Answer) फोन को भेजना
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }

    def process_player_input(self, player_id: str, input_data: str):
        """फोन से आए कंट्रोलर डेटा (जैसे 'MOVE_FORWARD') को डिकोड करना"""
        try:
            data = json.loads(input_data)
            # यह डेटा सीधा हमारे 'Physics Agent' या 'Multiplayer Nexus' को जाएगा
            # print(f"[INPUT RECEIVED]: Player {player_id} action -> {data}")
        except json.JSONDecodeError:
            pass

    async def close_stream(self, player_id: str):
        """प्लेयर के ऑफलाइन होने पर कनेक्शन काटना ताकि सर्वर की रैम (RAM) फ्री हो जाए"""
        if player_id in self.active_connections:
            await self.active_connections[player_id].close()
            del self.active_connections[player_id]
            print(f"[PIXEL STREAM]: Connection closed and memory freed for {player_id}.")
              
