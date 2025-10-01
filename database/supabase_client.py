"""
Supabase клиент для Ryabot Island
Полная замена asyncpg на официальный Supabase Python SDK
"""
import os
import logging
from typing import Optional, Dict, List, Any, Union
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Менеджер подключения к Supabase"""

    def __init__(self):
        self.client: Optional[Client] = None
        self._initialized = False

    def initialize(self):
        """Инициализация Supabase клиента"""
        if self._initialized:
            return

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть установлены в .env")

        try:
            self.client = create_client(url, key)
            self._initialized = True
            logger.info("✅ Supabase клиент инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Supabase: {e}")
            raise

    def get_client(self) -> Client:
        """Получить клиент Supabase"""
        if not self._initialized or not self.client:
            self.initialize()
        return self.client

    async def execute_query(self, table: str, operation: str, data: Dict = None,
                          filters: Dict = None, select: str = "*",
                          single: bool = False) -> Any:
        """
        Универсальный метод для выполнения запросов к Supabase

        Args:
            table: имя таблицы
            operation: тип операции (select, insert, update, delete, upsert)
            data: данные для операции
            filters: фильтры для запроса
            select: поля для выборки
            single: вернуть одну запись или все
        """
        try:
            client = self.get_client()
            query = client.table(table)

            if operation == "select":
                query = query.select(select)
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, dict) and 'operator' in value:
                            # Поддержка сложных операторов: {'operator': 'gte', 'value': 18}
                            op = value['operator']
                            val = value['value']
                            if op == 'gte':
                                query = query.gte(key, val)
                            elif op == 'lte':
                                query = query.lte(key, val)
                            elif op == 'gt':
                                query = query.gt(key, val)
                            elif op == 'lt':
                                query = query.lt(key, val)
                            elif op == 'neq':
                                query = query.neq(key, val)
                            elif op == 'in':
                                query = query.in_(key, val)
                        else:
                            query = query.eq(key, value)

                if single:
                    query = query.single()

                response = query.execute()
                return response.data[0] if single and response.data else response.data

            elif operation == "insert":
                response = query.insert(data).execute()
                return response.data[0] if response.data else None

            elif operation == "update":
                query = query.update(data)
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                response = query.execute()
                return response.data

            elif operation == "delete":
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                response = query.delete().execute()
                return response.data

            elif operation == "upsert":
                response = query.upsert(data).execute()
                return response.data

            elif operation == "count":
                query = query.select("*", count="exact")
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                response = query.execute()
                return response.count

        except Exception as e:
            logger.error(f"Ошибка Supabase запроса: {e} | Table: {table} | Operation: {operation}")
            return None

    async def execute_rpc(self, function_name: str, params: Dict = None) -> Any:
        """Выполнение RPC функций в Supabase"""
        try:
            client = self.get_client()
            response = client.rpc(function_name, params or {}).execute()
            return response.data
        except Exception as e:
            logger.error(f"Ошибка RPC: {e} | Function: {function_name}")
            return None

# Глобальный экземпляр менеджера
supabase_manager = SupabaseManager()

# Функции для обратной совместимости
async def execute_db(query_type: str = "select", table: str = "", **kwargs):
    """Обертка для совместимости со старым кодом"""
    return await supabase_manager.execute_query(table, query_type, **kwargs)

def get_supabase_client() -> Client:
    """Получить Supabase клиент"""
    return supabase_manager.get_client()
