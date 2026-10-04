// Shapes of the data the backend sends. These match backend/main.py.

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  price: number;
  image_url: string;
  total_stock: number;
}

export interface SizeStock {
  size: string;
  quantity: number;
}

export interface ProductDetail extends Product {
  inventory: SizeStock[];
}

/** Matches ChatResponse in backend/models.py. */
export interface ChatReply {
  reply: string;
  products: { product_id: string; name: string; price: number }[];
}

/** The only user details the backend sends to the browser. */
export interface User {
  first_name: string;
  last_name: string;
}
