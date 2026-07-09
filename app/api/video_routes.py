import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.jwt import verify_token
from app.core.logger import get_logger
from app.core.dependecy import current_user
from app.services.video_service import video_connection_manager, VideoService
from app.schema.video import RoomCreate

logger = get_logger(__name__)

router = APIRouter(prefix="/video", tags=["Video Call"])


@router.post("/rooms", summary="Create a new call room")
async def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    curr_user: dict = Depends(current_user)
):
    """
    Creates a new call room for WebRTC signaling.
    """
    video_service = VideoService(None, db)
    return await video_service.create_room(payload, curr_user.get("id"))


@router.get("/rooms", summary="List active call rooms")
async def list_rooms(
    db: Session = Depends(get_db),
    curr_user: dict = Depends(current_user)
):
    """
    List all active call rooms in the system.
    """
    video_service = VideoService(None, db)
    return await video_service.list_active_rooms(curr_user.get("id"))


@router.get("/rooms/{room_code}", summary="Get call room details")
async def get_room_details(
    room_code: str,
    db: Session = Depends(get_db),
    curr_user: dict = Depends(current_user)
):
    """
    Retrieve metadata details for a specific call room code.
    """
    video_service = VideoService(None, db)
    return await video_service.get_room_details(room_code)


@router.websocket("/ws/{room_code}")
async def websocket_signaling_endpoint(
    websocket: WebSocket,
    room_code: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for WebRTC signaling.
    Requires token in query parameter for authentication.
    """
    # 1. Verify token
    try:
        payload = verify_token(token)
        user_id = payload.get("id")
        email = payload.get("email")
        if not user_id or not email:
            raise Exception("Invalid session token payload")
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Authentication failed"
        }))
        await websocket.close(code=4001)
        return

    # 2. Verify call room exists and is active
    video_service = VideoService(None, db)
    room = video_service.room_repo.get_by_code(room_code)
    if not room:
        logger.warning(f"WebSocket join failed: Room {room_code} not found or inactive")
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Call room not found"
        }))
        await websocket.close(code=4004)
        return

    # 3. Add to connection manager
    user_info = {
        "user_id": user_id,
        "email": email,
        "name": email.split("@")[0]
    }
    
    await video_connection_manager.connect(room_code, user_id, websocket, user_info)
    
    try:
        while True:
            # Wait for message
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
            except Exception:
                continue
            
            msg_type = data.get("type")
            target = data.get("target")  # Specific user ID to direct signaling to
            
            outgoing_payload = {
                "type": msg_type,
                "sender": user_id,
                "sender_info": user_info,
                "data": data.get("data"),
                "target": target
            }
            
            if target:
                # Direct route
                await video_connection_manager.send_to_user(room_code, target, outgoing_payload)
            else:
                # Broadcast
                await video_connection_manager.broadcast_to_room(room_code, outgoing_payload, exclude_user_id=user_id)
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket routing loop encountered error: {e}")
    finally:
        video_connection_manager.disconnect(room_code, user_id)
