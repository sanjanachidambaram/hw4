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

/** The fields a product card needs. Both full products and chat results have them. */
export type CardProduct = Pick<
  Product,
  "product_id" | "name" | "price" | "description" | "image_url" | "total_stock"
>;

/** Matches ChatResponse in backend/models.py, after checking (see parseChatReply in api.ts). */
export interface ChatReply {
  reply: string;
  products: CardProduct[];
}

/** The only user details the backend sends to the browser. */
export interface User {
  first_name: string;
  last_name: string;
}
