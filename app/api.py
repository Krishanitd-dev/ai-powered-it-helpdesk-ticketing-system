from fastapi import APIRouter, Request, HTTPException, status  
from app.database import get_connection
from pydantic import BaseModel, Field 
from datetime import datetime
from typing import Literal

api_router = APIRouter(prefix="/api")
class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    priority: str = Field(min_length=1, max_length=20)
    description: str = Field(min_length=1, max_length=300)



class TicketUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Closed"] | None = None
    priority: Literal["Low", "Medium", "High"] | None = None
   
class TicketResponse(BaseModel):
    id: int
    subject: str
    category: str
    priority: str
    status: str
    created_at: datetime | None = None


class TicketResponseMessage(BaseModel):
    ticket_id: int
    content: str


class TicketUpdateResponse(BaseModel):
    id: int
    subject: str
    category: str
    priority: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )
    status: str | None = Field(default=None,
        min_length=1,
        max_length=20
    )
    created_at: datetime | None = None

class ResponseCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)



def require_user(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    return request.session["user_id"]

def require_helpdesk(request: Request):
    if "helpdesk_id" not in request.session:
        raise HTTPException(
            status_code=401,
            detail="Support staff authentication required"
        )

    return request.session["helpdesk_id"]

@api_router.get("/tickets",
                response_model=list[TicketResponse])
async def get_my_tickets(request: Request):

    user_id = require_user(request)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            subject,
            category,
            priority,
            status,
            created_at
        FROM tickets
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
            {
                "id": ticket[0],
                "subject": ticket[1],
                "category": ticket[2],
                "priority": ticket[3],
                "status": ticket[4],
                "created_at": ticket[5]
            }
            for ticket in tickets
        ]

@api_router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(ticket_id: int, request: Request):

    user_id = require_user(request)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, subject, category, priority, status, created_at
        FROM tickets
        WHERE id = %s AND user_id = %s
        """,
        (ticket_id, user_id)
    )

    ticket = cursor.fetchone()

    cursor.close()
    conn.close()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "id": ticket[0],
        "subject": ticket[1],
        "category": ticket[2],
        "priority": ticket[3],
        "status": ticket[4],
        "created_at": ticket[5]
    }
    

@api_router.post("/tickets", response_model=TicketResponse,
                 status_code=status.HTTP_201_CREATED)
async def create_ticket_api(
    request: Request,
    ticket: TicketCreate
):
    user_id = require_user(request)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (
            user_id,
            subject,
            category,
            priority,
            description
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, subject, category, priority, status, created_at
    """, (
        user_id,
        ticket.subject,
        ticket.category,
        ticket.priority,
        ticket.description
    ))

    new_ticket = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": new_ticket[0],
        "subject": new_ticket[1],
        "category": new_ticket[2],
        "priority": new_ticket[3],
        "status": new_ticket[4],
        "created_at": new_ticket[5]
       
    }

@api_router.patch("/tickets/{ticket_id}",  response_model=TicketUpdateResponse)
async def update_ticket_api(
    request: Request,
    ticket_id: int,
    ticket: TicketUpdate
):
    require_helpdesk(request)

    if ticket.status is None and ticket.priority is None:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    existing_ticket = cursor.fetchone()

    if not existing_ticket:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    cursor.execute(
        """
        UPDATE tickets
        SET status = COALESCE(%s, status),
            priority = COALESCE(%s, priority)
        WHERE id = %s
        RETURNING id, subject, category, priority, status, created_at
        """,
        (
            ticket.status,
            ticket.priority,
            ticket_id
        )
    )

    updated_ticket = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": updated_ticket[0],
        "subject": updated_ticket[1],
        "category": updated_ticket[2],
        "priority": updated_ticket[3],
        "status": updated_ticket[4],
        "created_at": updated_ticket[5]
    }

  

@api_router.delete(
    "/tickets/{ticket_id}",
    status_code=204
)
async def delete_ticket_api(
    request: Request,
    ticket_id: int
):
    user_id = require_user(request)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tickets
        WHERE id = %s
        AND user_id = %s
        RETURNING id
        """,
        (ticket_id, user_id)
    )

    deleted_ticket = cursor.fetchone()

    if not deleted_ticket:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    conn.commit()

    cursor.close()
    conn.close()

    return None

@api_router.get("/tickets/{ticket_id}/responses", response_model=list[TicketResponseMessage])
async def get_ticket_responses(
    request: Request,
    ticket_id: int
):
    user_id = require_user(request)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, response
        FROM tickets
        WHERE id = %s
        AND user_id = %s
        """,
        (ticket_id, user_id)
    )

    ticket = cursor.fetchone()

    cursor.close()
    conn.close()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if not ticket[1]:
        return []

    return [
        {
            "ticket_id": ticket[0],
            "content": ticket[1]
        }
    ]

@api_router.post("/tickets/{ticket_id}/responses", response_model=TicketResponseMessage)
async def create_ticket_response(
    request: Request,
    ticket_id: int,
    response: ResponseCreate
):
    require_helpdesk(request)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if not ticket:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    cursor.execute(
        """
        UPDATE tickets
        SET response = %s,
            status = 'In Progress'
        WHERE id = %s
        RETURNING id, response, status
        """,
        (
            response.content,
            ticket_id
        )
    )

    updated_ticket = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "ticket_id": updated_ticket[0],
        "content": updated_ticket[1]
       
    }