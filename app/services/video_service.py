import json
import asyncio
from typing import Dict, List, Any
from fastapi import WebSocket, HTTPException, Request
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.message import ErrorMessage, SuccessMessage
from app.core.response import success_response
from app.db.models.call_room import CallRoom
from app.repository.call_room_repository import CallRoomRepository
from app.schema.video import RoomCreate, RoomResponse
from app.common.utils import generate_room_code

logger = get_logger(__name__)


class VideoConnectionManager:
    def __init__(self):
        # Maps room_code -> Dict of user_id -> WebSocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Maps room_code -> Dict of user_id -> User Info
        self.room_users: Dict[str, Dict[str, dict]] = {}

    async def connect(self, room_code: str, user_id: str, websocket: WebSocket, user_info: dict):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}
            self.room_users[room_code] = {}
        
        self.active_connections[room_code][user_id] = websocket
        self.room_users[room_code][user_id] = user_info

        # 1. Notify others in the room that a new peer has joined
        await self.broadcast_to_room(
            room_code,
            {
                "type": "peer-joined",
                "sender": user_id,
                "user_info": user_info
            },
            exclude_user_id=user_id
        )
        
        # 2. Send current participants list to the joining user
        participants = list(self.room_users[room_code].values())
        await websocket.send_text(json.dumps({
            "type": "room-welcome",
            "sender": "system",
            "participants": participants
        }))

        logger.info(f"User {user_id} joined room {room_code}. Active participants count: {len(self.active_connections[room_code])}")

    def disconnect(self, room_code: str, user_id: str):
        if room_code in self.active_connections:
            if user_id in self.active_connections[room_code]:
                del self.active_connections[room_code][user_id]
            if user_id in self.room_users[room_code]:
                del self.room_users[room_code][user_id]
            
            # Clean up the room mapping if empty
            if not self.active_connections[room_code]:
                if room_code in self.active_connections:
                    del self.active_connections[room_code]
                if room_code in self.room_users:
                    del self.room_users[room_code]
                logger.info(f"Room {room_code} is empty, cleaned up.")
            else:
                # Notify remaining peers that this peer has left
                asyncio.create_task(self.broadcast_to_room(
                    room_code,
                    {
                        "type": "peer-left",
                        "sender": user_id
                    }
                ))
                logger.info(f"User {user_id} disconnected from room {room_code}")

    async def send_to_user(self, room_code: str, target_user_id: str, message: dict):
        if room_code in self.active_connections and target_user_id in self.active_connections[room_code]:
            ws = self.active_connections[room_code][target_user_id]
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to user {target_user_id} in room {room_code}: {e}")
                self.disconnect(room_code, target_user_id)

    async def broadcast_to_room(self, room_code: str, message: dict, exclude_user_id: str | None = None):
        if room_code in self.active_connections:
            message_str = json.dumps(message)
            for uid, ws in list(self.active_connections[room_code].items()):
                if exclude_user_id is None or uid != exclude_user_id:
                    try:
                        await ws.send_text(message_str)
                    except Exception as e:
                        logger.error(f"Failed to broadcast message to {uid} in room {room_code}: {e}")
                        self.disconnect(room_code, uid)


# Global connection manager instance
video_connection_manager = VideoConnectionManager()


class VideoService:
    def __init__(self, request: Request | None, db: Session):
        self.request = request
        self.db = db
        self.room_repo = CallRoomRepository(self.db)

    async def create_room(self, payload: RoomCreate, current_user_id: str):
        """
        Creates a new call room.
        """
        room_code = generate_room_code()
        
        # Verify code is unique
        while self.room_repo.get_by_code(room_code) is not None:
            room_code = generate_room_code()

        room_data = {
            "room_code": room_code,
            "name": payload.name or f"Meeting by User {current_user_id[:8]}",
            "host_id": current_user_id,
            "is_active": True
        }

        db_room = self.room_repo.create(room_data)
        
        # Format response
        response_data = RoomResponse.model_validate(db_room)
        
        return success_response(
            status_code=http_status.HTTP_201_CREATED,
            msg=SuccessMessage.ROOM_CREATED_SUCCESSFULLY,
            data=response_data.model_dump()
        )

    async def get_room_details(self, room_code: str):
        """
        Retrieve details for a single room.
        """
        db_room = self.room_repo.get_by_code(room_code)
        if not db_room:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=ErrorMessage.ROOM_NOT_FOUND
            )

        response_data = RoomResponse.model_validate(db_room)

        return success_response(
            status_code=http_status.HTTP_200_OK,
            msg=SuccessMessage.ROOM_FETCHED_SUCCESSFULLY,
            data=response_data.model_dump()
        )

    async def list_active_rooms(self, current_user_id: str):
        """
        Lists all active call rooms.
        """
        rooms = self.room_repo.get_all(filters={"is_active": True})
        
        # Convert to response format
        response_list = [RoomResponse.model_validate(r).model_dump() for r in rooms]

        return success_response(
            status_code=http_status.HTTP_200_OK,
            msg=SuccessMessage.RESPONSE_FETCHED_SUCCESSFULLY,
            data=response_list
        )
