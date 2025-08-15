import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from schemas.product_color import ProductColor, ProductColorCreate
from db.supabase_db import supabase

class ProductColorRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[ProductColor]:
        pass

    @abstractmethod
    def get_by_id(self, color_id: uuid.UUID) -> Optional[ProductColor]:
        pass

    @abstractmethod
    def create(self, color_data: ProductColorCreate) -> ProductColor:
        pass

    @abstractmethod
    def update(self, color_id: uuid.UUID, color_data: ProductColorCreate) -> Optional[ProductColor]:
        pass

    @abstractmethod
    def delete(self, color_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    def get_all(self) -> List[ProductColor]:
        pass

class SupabaseProductColorRepository(ProductColorRepository):
    TABLE_NAME = "product_colors"
    
    def get_all(self) -> List[ProductColor]:
        response = supabase.table(self.TABLE_NAME).select("*").execute()
        return [ProductColor(**item) for item in response.data] if response.data else []


    def _prepare_data(self, pydantic_model: BaseModel) -> dict:
        data_dict = pydantic_model.dict()
        for key, value in data_dict.items():
            if isinstance(value, uuid.UUID):
                data_dict[key] = str(value)
        return data_dict

    def get_all(self) -> List[ProductColor]:
        response = supabase.table(self.TABLE_NAME).select("*").execute()
        return [ProductColor(**item) for item in response.data] if response.data else []

    def get_by_id(self, color_id: uuid.UUID) -> Optional[ProductColor]:
        response = supabase.table(self.TABLE_NAME).select("*").eq("id", str(color_id)).execute()
        return ProductColor(**response.data[0]) if response.data else None

    def create(self, color_data: ProductColorCreate) -> ProductColor:
        data_to_insert = self._prepare_data(color_data)
        response = supabase.table(self.TABLE_NAME).insert(data_to_insert).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create product color.")
        return ProductColor(**response.data[0])

    def update(self, color_id: uuid.UUID, color_data: ProductColorCreate) -> Optional[ProductColor]:
        data_to_update = self._prepare_data(color_data)
        response = supabase.table(self.TABLE_NAME).update(data_to_update).eq("id", str(color_id)).execute()
        return ProductColor(**response.data[0]) if response.data else None

    def delete(self, color_id: uuid.UUID) -> bool:
        response = supabase.table(self.TABLE_NAME).delete().eq("id", str(color_id)).execute()
        return bool(response.data)