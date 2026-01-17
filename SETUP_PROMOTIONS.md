# Promotions Feature - Quick Setup Guide

## Installation Steps

### 1. The promotions app has been created and added to your project

The following has been completed:
- ✅ Created `promotions` app with all necessary files
- ✅ Added `promotions` to `INSTALLED_APPS` in settings.py
- ✅ Added promotions URLs to main urls.py
- ✅ Updated Product serializer to include promotion data
- ✅ Updated Product viewset to optimize promotion queries

### 2. Run Database Migrations

You need to run migrations to create the promotion tables:

```bash
# Make sure you're in the manymor_backend directory and your virtual environment is activated
cd manymor_backend
python manage.py makemigrations promotions
python manage.py migrate
```

### 3. Create a Superuser (if you haven't already)

```bash
python manage.py createsuperuser
```

### 4. (Optional) Create Sample Promotions for Testing

```bash
python manage.py create_sample_promotions
```

This will create two sample product promotions that you can see in action.

### 5. Access the Admin Panel

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to `http://localhost:8000/admin/`

3. Log in with your superuser credentials

4. You'll see two new sections:
   - **Carousel Promotions** - For managing homepage banners
   - **Product Promotions** - For managing product discounts

## Quick Test

### Test Carousel Promotions API

```bash
# Get all carousel promotions
curl http://localhost:8000/api/promotions/carousel-promotions/

# Get only active carousel promotions
curl http://localhost:8000/api/promotions/carousel-promotions/active/
```

### Test Product Promotions API

```bash
# Get all product promotions
curl http://localhost:8000/api/promotions/product-promotions/

# Get only active product promotions
curl http://localhost:8000/api/promotions/product-promotions/active/
```

### Test Product API with Promotion Data

```bash
# Get products (they now include promotion information)
curl http://localhost:8000/api/products/
```

You should see fields like `has_promotion`, `promotional_price`, `active_promotion`, etc.

## Creating Your First Carousel Promotion

### Via Admin Panel:

1. Go to `http://localhost:8000/admin/promotions/carouselpromotion/`
2. Click "Add Carousel Promotion"
3. Fill in:
   - **Title**: "Summer Sale 2026"
   - **Description**: "Get up to 50% off on all summer items!"
   - **Image**: Upload a banner image (recommended size: 1920x600px)
   - **Button Text**: "Shop Now"
   - **Link URL**: Leave blank or add a URL
   - **Is Active**: Check this
   - **Display Order**: 1
   - **Start Date**: Today's date
   - **End Date**: A future date
4. Click "Save"

### Via API (using curl or Postman):

```bash
curl -X POST http://localhost:8000/api/promotions/carousel-promotions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Summer Sale 2026" \
  -F "description=Get up to 50% off on all summer items!" \
  -F "image=@/path/to/your/banner.jpg" \
  -F "button_text=Shop Now" \
  -F "is_active=true" \
  -F "display_order=1" \
  -F "start_date=2026-01-17T00:00:00Z" \
  -F "end_date=2026-12-31T23:59:59Z"
```

## Creating Your First Product Promotion

### Via Admin Panel:

1. Go to `http://localhost:8000/admin/promotions/productpromotion/`
2. Click "Add Product Promotion"
3. Fill in:
   - **Name**: "Winter Clearance"
   - **Description**: "20% off all winter clothing"
   - **Discount Type**: Percentage
   - **Discount Value**: 20
   - **Badge Text**: "20% OFF"
   - **Badge Color**: #FF0000
   - **Products**: Select products from the list
   - **Is Active**: Check this
   - **Start Date**: Today's date
   - **End Date**: A future date
4. Click "Save"

### Via API:

```bash
curl -X POST http://localhost:8000/api/promotions/product-promotions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Winter Clearance",
    "description": "20% off all winter clothing",
    "discount_type": "percentage",
    "discount_value": 20.00,
    "badge_text": "20% OFF",
    "badge_color": "#FF0000",
    "is_active": true,
    "start_date": "2026-01-17T00:00:00Z",
    "end_date": "2026-12-31T23:59:59Z",
    "products": [1, 2, 3]
  }'
```

## Frontend Integration

### For Angular Frontend:

1. **Create a Promotion Service:**

```typescript
// promotion.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PromotionService {
  private apiUrl = 'http://localhost:8000/api/promotions';

  constructor(private http: HttpClient) { }

  getActiveCarouselPromotions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/carousel-promotions/active/`);
  }

  getActiveProductPromotions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/product-promotions/active/`);
  }
}
```

2. **In your homepage component:**

```typescript
// home.component.ts
export class HomeComponent implements OnInit {
  carouselPromotions: any[] = [];

  constructor(private promotionService: PromotionService) { }

  ngOnInit() {
    this.promotionService.getActiveCarouselPromotions().subscribe(
      promotions => {
        this.carouselPromotions = promotions;
      }
    );
  }
}
```

3. **In your product card component, promotion data is already included:**

```typescript
// Products now automatically have promotion fields
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
```

## Troubleshooting

### Issue: "No module named 'promotions'"
**Solution**: Make sure you've added `'promotions'` to `INSTALLED_APPS` in settings.py

### Issue: "Table doesn't exist"
**Solution**: Run migrations:
```bash
python manage.py makemigrations promotions
python manage.py migrate
```

### Issue: "Permission denied" when creating promotions via API
**Solution**: Make sure you're authenticated as an admin user (is_staff=True)

### Issue: Images not displaying
**Solution**: Make sure MEDIA_URL and MEDIA_ROOT are configured in settings.py and that you're serving media files in development

## Next Steps

1. ✅ Run migrations
2. ✅ Create some carousel promotions in admin panel
3. ✅ Create product promotions and assign products
4. ✅ Test the APIs
5. ✅ Integrate with your Angular frontend
6. ✅ Style the carousel and promotion badges in your frontend

For detailed API documentation and examples, see `PROMOTIONS_README.md`
