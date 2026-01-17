# Promotion Management for Custom Admin Users

## Overview
This guide is for managing promotions using your **custom admin users** (users with `role='ADMIN'`) through the API, not the Django admin panel.

## Authentication

All promotion management endpoints require:
1. **Authentication**: Valid JWT token
2. **Authorization**: User must have `role='ADMIN'`

### Example Authentication Header:
```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints for Admin Users

### Dashboard - Promotion Statistics

**Get promotion statistics (Admin Dashboard)**
```
GET /api/admin/promotions/stats/
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "active_carousel_promotions": 3,
  "active_product_promotions": 5,
  "upcoming_promotions": 2,
  "recently_expired_promotions": 1,
  "products_with_promotions": 15
}
```

### Carousel Promotions Management

#### Create Carousel Promotion
```
POST /api/promotions/carousel-promotions/
Authorization: Bearer <admin-token>
Content-Type: multipart/form-data

Form Data:
- title: "Summer Sale 2026"
- description: "Get up to 50% off on all summer items!"
- image: <file>
- button_text: "Shop Now"
- link_url: "https://yourstore.com/summer-sale"
- is_active: true
- display_order: 1
- start_date: "2026-06-01T00:00:00Z"
- end_date: "2026-08-31T23:59:59Z"
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "title": "Summer Sale 2026",
  "description": "Get up to 50% off on all summer items!",
  "image": "http://localhost:8000/media/promotions/carousel/banner.jpg",
  "link_url": "https://yourstore.com/summer-sale",
  "button_text": "Shop Now",
  "is_active": true,
  "display_order": 1,
  "start_date": "2026-06-01T00:00:00Z",
  "end_date": "2026-08-31T23:59:59Z",
  "is_currently_active": false
}
```

**Error Response (403 Forbidden) - Non-admin user:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### Update Carousel Promotion
```
PATCH /api/promotions/carousel-promotions/{id}/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "is_active": false,
  "display_order": 5
}
```

#### Delete Carousel Promotion
```
DELETE /api/promotions/carousel-promotions/{id}/
Authorization: Bearer <admin-token>
```

#### List All Carousel Promotions
```
GET /api/promotions/carousel-promotions/
Authorization: Bearer <admin-token>
```

### Product Promotions Management

#### Create Product Promotion
```
POST /api/promotions/product-promotions/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "name": "Winter Clearance Sale",
  "description": "20% off all winter clothing",
  "discount_type": "percentage",
  "discount_value": 20.00,
  "badge_text": "20% OFF",
  "badge_color": "#FF0000",
  "is_active": true,
  "start_date": "2026-01-17T00:00:00Z",
  "end_date": "2026-02-28T23:59:59Z",
  "products": [1, 2, 3, 4, 5]
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "name": "Winter Clearance Sale",
  "description": "20% off all winter clothing",
  "discount_type": "percentage",
  "discount_value": "20.00",
  "badge_text": "20% OFF",
  "badge_color": "#FF0000",
  "is_active": true,
  "start_date": "2026-01-17T00:00:00Z",
  "end_date": "2026-02-28T23:59:59Z",
  "is_currently_active": true,
  "products_count": 5
}
```

#### Update Product Promotion
```
PATCH /api/promotions/product-promotions/{id}/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "discount_value": 25.00,
  "badge_text": "25% OFF"
}
```

#### Add Products to Promotion
```
POST /api/promotions/product-promotions/{id}/add_products/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "product_ids": [6, 7, 8]
}
```

**Success Response:**
```json
{
  "id": 1,
  "name": "Winter Clearance Sale",
  "products_count": 8
  // ... other fields
}
```

#### Remove Products from Promotion
```
POST /api/promotions/product-promotions/{id}/remove_products/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "product_ids": [6, 7]
}
```

#### Delete Product Promotion
```
DELETE /api/promotions/product-promotions/{id}/
Authorization: Bearer <admin-token>
```

### Public Endpoints (No Authentication Required)

#### Get Active Carousel Promotions (for frontend display)
```
GET /api/promotions/carousel-promotions/active/
```

#### Get Active Product Promotions
```
GET /api/promotions/product-promotions/active/
```

#### Get Products with Promotion Info
```
GET /api/products/
```
Products automatically include promotion data:
```json
{
  "id": 1,
  "name": "Winter Jacket",
  "price": "99.99",
  "has_promotion": true,
  "active_promotion": {
    "id": 1,
    "name": "Winter Clearance Sale",
    "badge_text": "20% OFF",
    "badge_color": "#FF0000"
  },
  "promotional_price": "79.99",
  "discount_percentage": 20.0
}
```

## Permission Requirements

### Public Access (No Auth):
- ✅ View active carousel promotions
- ✅ View active product promotions
- ✅ View products with promotion info
- ✅ List all promotions (read-only)

### Admin Access (role='ADMIN' required):
- ✅ Create carousel promotions
- ✅ Update carousel promotions
- ✅ Delete carousel promotions
- ✅ Create product promotions
- ✅ Update product promotions
- ✅ Delete product promotions
- ✅ Add products to promotions
- ✅ Remove products from promotions
- ✅ View promotion statistics

## Frontend Integration (Angular)

### Admin Service Example

```typescript
// services/admin-promotion.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminPromotionService {
  private apiUrl = `${environment.apiUrl}/promotions`;
  private dashboardUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) { }

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  // Dashboard Stats
  getPromotionStats(): Observable<any> {
    return this.http.get(
      `${this.dashboardUrl}/promotions/stats/`,
      { headers: this.getAuthHeaders() }
    );
  }

  // Carousel Promotions
  createCarouselPromotion(formData: FormData): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/carousel-promotions/`,
      formData,
      { headers: this.getAuthHeaders() }
    );
  }

  updateCarouselPromotion(id: number, data: any): Observable<any> {
    return this.http.patch(
      `${this.apiUrl}/carousel-promotions/${id}/`,
      data,
      { headers: this.getAuthHeaders() }
    );
  }

  deleteCarouselPromotion(id: number): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/carousel-promotions/${id}/`,
      { headers: this.getAuthHeaders() }
    );
  }

  // Product Promotions
  createProductPromotion(data: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/product-promotions/`,
      data,
      { headers: this.getAuthHeaders() }
    );
  }

  updateProductPromotion(id: number, data: any): Observable<any> {
    return this.http.patch(
      `${this.apiUrl}/product-promotions/${id}/`,
      data,
      { headers: this.getAuthHeaders() }
    );
  }

  addProductsToPromotion(promotionId: number, productIds: number[]): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/product-promotions/${promotionId}/add_products/`,
      { product_ids: productIds },
      { headers: this.getAuthHeaders() }
    );
  }

  removeProductsFromPromotion(promotionId: number, productIds: number[]): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/product-promotions/${promotionId}/remove_products/`,
      { product_ids: productIds },
      { headers: this.getAuthHeaders() }
    );
  }

  deleteProductPromotion(id: number): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/product-promotions/${id}/`,
      { headers: this.getAuthHeaders() }
    );
  }

  // List promotions
  getAllCarouselPromotions(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/carousel-promotions/`,
      { headers: this.getAuthHeaders() }
    );
  }

  getAllProductPromotions(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/product-promotions/`,
      { headers: this.getAuthHeaders() }
    );
  }
}
```

### Admin Component Example

```typescript
// components/admin/promotion-management/promotion-management.component.ts
import { Component, OnInit } from '@angular/core';
import { AdminPromotionService } from '../../../services/admin-promotion.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-promotion-management',
  templateUrl: './promotion-management.component.html',
  styleUrls: ['./promotion-management.component.scss']
})
export class PromotionManagementComponent implements OnInit {
  carouselPromotions: any[] = [];
  productPromotions: any[] = [];
  stats: any = {};
  
  carouselForm: FormGroup;
  productPromotionForm: FormGroup;
  
  selectedImage: File | null = null;
  isLoading = false;

  constructor(
    private adminPromotionService: AdminPromotionService,
    private fb: FormBuilder
  ) {
    this.carouselForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      button_text: [''],
      link_url: [''],
      is_active: [true],
      display_order: [1],
      start_date: ['', Validators.required],
      end_date: ['', Validators.required]
    });

    this.productPromotionForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      discount_type: ['percentage', Validators.required],
      discount_value: [0, [Validators.required, Validators.min(0)]],
      badge_text: [''],
      badge_color: ['#FF0000'],
      is_active: [true],
      start_date: ['', Validators.required],
      end_date: ['', Validators.required],
      products: [[]]
    });
  }

  ngOnInit(): void {
    this.loadPromotionStats();
    this.loadCarouselPromotions();
    this.loadProductPromotions();
  }

  loadPromotionStats(): void {
    this.adminPromotionService.getPromotionStats().subscribe({
      next: (stats) => {
        this.stats = stats;
      },
      error: (error) => {
        console.error('Error loading promotion stats:', error);
      }
    });
  }

  loadCarouselPromotions(): void {
    this.adminPromotionService.getAllCarouselPromotions().subscribe({
      next: (promotions) => {
        this.carouselPromotions = promotions;
      },
      error: (error) => {
        console.error('Error loading carousel promotions:', error);
      }
    });
  }

  loadProductPromotions(): void {
    this.adminPromotionService.getAllProductPromotions().subscribe({
      next: (promotions) => {
        this.productPromotions = promotions;
      },
      error: (error) => {
        console.error('Error loading product promotions:', error);
      }
    });
  }

  onImageSelected(event: any): void {
    this.selectedImage = event.target.files[0];
  }

  createCarouselPromotion(): void {
    if (this.carouselForm.valid && this.selectedImage) {
      this.isLoading = true;
      const formData = new FormData();
      
      Object.keys(this.carouselForm.value).forEach(key => {
        formData.append(key, this.carouselForm.value[key]);
      });
      
      formData.append('image', this.selectedImage);

      this.adminPromotionService.createCarouselPromotion(formData).subscribe({
        next: (promotion) => {
          console.log('Carousel promotion created:', promotion);
          this.loadCarouselPromotions();
          this.carouselForm.reset();
          this.selectedImage = null;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error creating carousel promotion:', error);
          this.isLoading = false;
        }
      });
    }
  }

  createProductPromotion(): void {
    if (this.productPromotionForm.valid) {
      this.isLoading = true;
      
      this.adminPromotionService.createProductPromotion(
        this.productPromotionForm.value
      ).subscribe({
        next: (promotion) => {
          console.log('Product promotion created:', promotion);
          this.loadProductPromotions();
          this.productPromotionForm.reset();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error creating product promotion:', error);
          this.isLoading = false;
        }
      });
    }
  }

  deleteCarouselPromotion(id: number): void {
    if (confirm('Are you sure you want to delete this carousel promotion?')) {
      this.adminPromotionService.deleteCarouselPromotion(id).subscribe({
        next: () => {
          console.log('Carousel promotion deleted');
          this.loadCarouselPromotions();
        },
        error: (error) => {
          console.error('Error deleting carousel promotion:', error);
        }
      });
    }
  }

  deleteProductPromotion(id: number): void {
    if (confirm('Are you sure you want to delete this product promotion?')) {
      this.adminPromotionService.deleteProductPromotion(id).subscribe({
        next: () => {
          console.log('Product promotion deleted');
          this.loadProductPromotions();
        },
        error: (error) => {
          console.error('Error deleting product promotion:', error);
        }
      });
    }
  }
}
```

## Testing with Postman/cURL

### 1. Login as Admin User
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "adminpassword"
  }'
```

Save the `access` token from response.

### 2. Create Carousel Promotion
```bash
curl -X POST http://localhost:8000/api/promotions/carousel-promotions/ \
  -H "Authorization: Bearer <your-token>" \
  -F "title=Summer Sale" \
  -F "description=Big summer discounts" \
  -F "image=@/path/to/banner.jpg" \
  -F "button_text=Shop Now" \
  -F "is_active=true" \
  -F "display_order=1" \
  -F "start_date=2026-06-01T00:00:00Z" \
  -F "end_date=2026-08-31T23:59:59Z"
```

### 3. Create Product Promotion
```bash
curl -X POST http://localhost:8000/api/promotions/product-promotions/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Winter Sale",
    "discount_type": "percentage",
    "discount_value": 20,
    "badge_text": "20% OFF",
    "badge_color": "#FF0000",
    "is_active": true,
    "start_date": "2026-01-17T00:00:00Z",
    "end_date": "2026-02-28T23:59:59Z",
    "products": [1, 2, 3]
  }'
```

### 4. Get Promotion Stats (Admin Dashboard)
```bash
curl -X GET http://localhost:8000/api/admin/promotions/stats/ \
  -H "Authorization: Bearer <your-token>"
```

## Error Handling

### 403 Forbidden - Non-admin user tries to create/update/delete:
```json
{
  "error": "Only admin users can modify promotions"
}
```

### 401 Unauthorized - No token or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request - Invalid data:
```json
{
  "field_name": ["This field is required."]
}
```

## Summary

✅ **Admin users** with `role='ADMIN'` can manage promotions via API  
✅ **No Django admin panel** required  
✅ **JWT authentication** for all admin operations  
✅ **Public read access** for frontend carousel and product display  
✅ **Dashboard integration** with promotion statistics  
✅ **Role-based permissions** matching your existing system  

Your custom admin users now have full control over promotions through the API!
