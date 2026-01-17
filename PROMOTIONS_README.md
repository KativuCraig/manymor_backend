# Promotions Feature Documentation

## Overview
This promotions feature allows administrators to create and manage two types of promotions:
1. **Carousel Promotions**: Banner images displayed in the frontend carousel
2. **Product Promotions**: Discounts applied to specific products

## Models

### CarouselPromotion
Promotional banners for the homepage carousel.

**Fields:**
- `title` - Banner title
- `description` - Detailed description
- `image` - Banner image (uploaded to `media/promotions/carousel/`)
- `link_url` - Optional URL when banner is clicked
- `button_text` - Text for call-to-action button
- `is_active` - Whether the promotion is active
- `display_order` - Order in carousel (lower numbers appear first)
- `start_date` - When promotion starts
- `end_date` - When promotion ends

### ProductPromotion
Discounts that can be applied to specific products.

**Fields:**
- `name` - Promotion name
- `description` - Detailed description
- `discount_type` - Either 'percentage' or 'fixed'
- `discount_value` - The discount amount (percentage or fixed price)
- `products` - Many-to-many relationship with products
- `badge_text` - Text displayed on product badge (e.g., "SALE", "20% OFF")
- `badge_color` - Hex color code for badge background
- `is_active` - Whether the promotion is active
- `start_date` - When promotion starts
- `end_date` - When promotion ends

## API Endpoints

### Carousel Promotions

**List all carousel promotions:**
```
GET /api/promotions/carousel-promotions/
```

**Get only active carousel promotions (for frontend display):**
```
GET /api/promotions/carousel-promotions/active/
```

**Get only currently active promotions with query parameter:**
```
GET /api/promotions/carousel-promotions/?active_only=true
```

**Get single carousel promotion:**
```
GET /api/promotions/carousel-promotions/{id}/
```

**Create carousel promotion (Admin only):**
```
POST /api/promotions/carousel-promotions/
Content-Type: multipart/form-data

{
  "title": "Summer Sale 2026",
  "description": "Get up to 50% off on selected items",
  "image": <file>,
  "link_url": "https://example.com/summer-sale",
  "button_text": "Shop Now",
  "is_active": true,
  "display_order": 1,
  "start_date": "2026-06-01T00:00:00Z",
  "end_date": "2026-08-31T23:59:59Z"
}
```

**Update carousel promotion (Admin only):**
```
PUT /api/promotions/carousel-promotions/{id}/
PATCH /api/promotions/carousel-promotions/{id}/
```

**Delete carousel promotion (Admin only):**
```
DELETE /api/promotions/carousel-promotions/{id}/
```

### Product Promotions

**List all product promotions:**
```
GET /api/promotions/product-promotions/
```

**Get only active product promotions:**
```
GET /api/promotions/product-promotions/active/
```

**Get only currently active promotions with query parameter:**
```
GET /api/promotions/product-promotions/?active_only=true
```

**Get single product promotion:**
```
GET /api/promotions/product-promotions/{id}/
```

**Create product promotion (Admin only):**
```
POST /api/promotions/product-promotions/
Content-Type: application/json

{
  "name": "Winter Clearance",
  "description": "20% off all winter clothing",
  "discount_type": "percentage",
  "discount_value": 20.00,
  "badge_text": "20% OFF",
  "badge_color": "#FF0000",
  "is_active": true,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-02-28T23:59:59Z",
  "products": [1, 2, 3]
}
```

**Add products to promotion (Admin only):**
```
POST /api/promotions/product-promotions/{id}/add_products/
Content-Type: application/json

{
  "product_ids": [4, 5, 6]
}
```

**Remove products from promotion (Admin only):**
```
POST /api/promotions/product-promotions/{id}/remove_products/
Content-Type: application/json

{
  "product_ids": [4, 5]
}
```

**Update product promotion (Admin only):**
```
PUT /api/promotions/product-promotions/{id}/
PATCH /api/promotions/product-promotions/{id}/
```

**Delete product promotion (Admin only):**
```
DELETE /api/promotions/product-promotions/{id}/
```

## Product API Integration

Products now include promotion information in their responses:

**Product Response Example:**
```json
{
  "id": 1,
  "name": "Winter Jacket",
  "description": "Warm winter jacket",
  "price": "99.99",
  "stock_quantity": 50,
  "is_active": true,
  "category": 1,
  "category_name": "Clothing",
  "images": [...],
  "created_at": "2026-01-01T00:00:00Z",
  "has_promotion": true,
  "active_promotion": {
    "id": 1,
    "name": "Winter Clearance",
    "badge_text": "20% OFF",
    "badge_color": "#FF0000"
  },
  "promotional_price": "79.99",
  "discount_percentage": 20.0
}
```

**New Product Fields:**
- `has_promotion` - Boolean indicating if product has active promotion
- `active_promotion` - Details of the active promotion (if any)
- `promotional_price` - Calculated discounted price (if promotion exists)
- `discount_percentage` - Discount percentage for display

## Admin Panel

### Managing Carousel Promotions
1. Navigate to `/admin/promotions/carouselpromotion/`
2. Click "Add Carousel Promotion"
3. Fill in the details:
   - Title and description
   - Upload banner image
   - Set button text and link URL
   - Configure display order
   - Set start and end dates
   - Mark as active
4. Save

### Managing Product Promotions
1. Navigate to `/admin/promotions/productpromotion/`
2. Click "Add Product Promotion"
3. Fill in the details:
   - Name and description
   - Select discount type (percentage or fixed)
   - Enter discount value
   - Set badge text and color
   - Select products to apply promotion to
   - Set start and end dates
   - Mark as active
4. Save

## Frontend Integration Guide

### Displaying Carousel Promotions

**Fetch active promotions:**
```javascript
// Fetch active carousel promotions
fetch('http://localhost:8000/api/promotions/carousel-promotions/active/')
  .then(response => response.json())
  .then(promotions => {
    // promotions is an array of active carousel banners
    // Use in your carousel component
    promotions.forEach(promo => {
      console.log(promo.title);
      console.log(promo.image); // URL to image
      console.log(promo.button_text);
      console.log(promo.link_url);
    });
  });
```

**Angular Example:**
```typescript
// In your service
getActiveCarouselPromotions(): Observable<CarouselPromotion[]> {
  return this.http.get<CarouselPromotion[]>(
    `${this.apiUrl}/promotions/carousel-promotions/active/`
  );
}

// In your component
ngOnInit() {
  this.promotionService.getActiveCarouselPromotions().subscribe(
    promotions => {
      this.carouselItems = promotions;
    }
  );
}
```

### Displaying Product Promotions

Products automatically include promotion data. In your product card component:

```typescript
// Product interface
interface Product {
  id: number;
  name: string;
  price: number;
  has_promotion: boolean;
  promotional_price?: number;
  discount_percentage?: number;
  active_promotion?: {
    badge_text: string;
    badge_color: string;
  };
}

// In your template
<div class="product-card">
  <div class="badge" 
       *ngIf="product.has_promotion"
       [style.background-color]="product.active_promotion.badge_color">
    {{ product.active_promotion.badge_text }}
  </div>
  
  <h3>{{ product.name }}</h3>
  
  <div class="price">
    <span class="original-price" 
          [class.strikethrough]="product.has_promotion">
      ${{ product.price }}
    </span>
    <span class="promo-price" *ngIf="product.has_promotion">
      ${{ product.promotional_price }}
    </span>
  </div>
  
  <div class="discount" *ngIf="product.has_promotion">
    Save {{ product.discount_percentage }}%!
  </div>
</div>
```

## Permissions

- **List/Retrieve**: Public (anyone can view)
- **Create/Update/Delete**: Admin only (requires `is_staff=True`)

## Database Migrations

After setting up the promotion feature, run migrations:

```bash
python manage.py makemigrations promotions
python manage.py migrate
```

## Media Files

Promotion images are stored in:
- Carousel promotions: `media/promotions/carousel/`

Make sure your `MEDIA_ROOT` and `MEDIA_URL` are properly configured in settings.py.

## Example Use Cases

### Use Case 1: Flash Sale Banner
1. Create a CarouselPromotion with eye-catching image
2. Set start_date to sale start time
3. Set end_date to sale end time
4. Link to a collection or product page
5. Banner automatically appears/disappears based on dates

### Use Case 2: Category-wide Discount
1. Create a ProductPromotion with 20% discount
2. Add all products from a specific category
3. Products automatically show discount badge and reduced price
4. Promotion applies for the specified date range

### Use Case 3: Limited Time Offer
1. Create both a CarouselPromotion (banner) and ProductPromotion (discount)
2. Same start/end dates for both
3. Link carousel banner to promoted products
4. Creates a cohesive promotional campaign

## Notes

- Promotions are automatically filtered by date range when using `active/` endpoints
- Multiple promotions can be applied to the same product (only first active one is used)
- Promotional prices are calculated in real-time based on current product price
- Badge colors should be hex codes (e.g., #FF0000 for red)
- Display order for carousel promotions determines the sequence (lower = first)
