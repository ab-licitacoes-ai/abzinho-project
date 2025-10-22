import os
import uuid
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import date, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional

from ..config.database import get_db_connection, N8N_WEBHOOK_URL

router = APIRouter(
    prefix="/tasks",
    tags=["Tarefas"],
)

# Pydantic models to validate and encript data
class TaskBase(BaseModel):
    descricao: str
    responsavel: str
    data_limite: date
    status: str
    prioridade: str
    observacoes: Optional[str] = None

class Task(TaskBase):
    """Modelo de resposta: garante que apenas os campos NÃO SENSÍVEIS sejam expostos."""
    task_id: uuid.UUID
    data_criacao: datetime

@router.get("", response_model=List[Task])
def get_all_tasks():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY data_limite DESC;")
            tasks = cursor.fetchall()
            return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar dados.")
    finally:
        if conn:
            conn.close()

@router.post("", response_model=Task, status_code=201)
def create_task(task: TaskBase):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO tasks (descricao, responsavel, data_limite, status, prioridade, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (task.descricao, task.responsavel, task.data_limite, task.status, task.prioridade, task.observacoes))
            
            new_task = cur.fetchone()
            conn.commit()

            return new_task

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar tarefa. Verifique os dados de entrada.")
    finally:
        if conn:
            conn.close()

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: uuid.UUID, task: TaskBase):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE tasks SET
                    descricao=%s, responsavel=%s, data_limite=%s, status=%s, prioridade=%s, observacoes=%s
                WHERE task_id = %s
                RETURNING *;
            """, (task.descricao, task.responsavel, task.data_limite, task.status, task.prioridade, task.observacoes, task_id))
            
            updated_task = cur.fetchone()
            if not updated_task:
                raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
            
            conn.commit()
            return updated_task

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Erro ao atualizar tarefa.")
    finally:
        if conn:
            conn.close()