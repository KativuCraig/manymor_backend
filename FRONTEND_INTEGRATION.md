# Frontend Integration Guide (Angular)

## TypeScript Interfaces

Create these interfaces in your Angular project:

```typescript
// models/promotion.model.ts

export interface CarouselPromotion {
  id: number;
  title: string;
  description: string;
  image: string;
  link_url?: string;
  button_text: string;
  is_active: boolean;
  display_order: number;
  start_date: string;
  end_date: string;
  is_currently_active: boolean;
}

export interface ProductPromotion {
  id: number;
  name: string;
  description: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  badge_text: string;
  badge_color: string;
  is_active: boolean;
  start_date: string;
  end_date: string;
  is_currently_active: boolean;
  products_count: number;
}

export interface ActivePromotion {
  id: number;
  name: string;
  badge_text: string;
  badge_color: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock_quantity: number;
  is_active: boolean;
  category: number;
  category_name: string;
  images: Array<{id: number; image: string}>;
  created_at: string;
  has_promotion: boolean;
  active_promotion?: ActivePromotion;
  promotional_price?: number;
  discount_percentage?: number;
}
```

## Service Layer

```typescript
// services/promotion.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { CarouselPromotion, ProductPromotion } from '../models/promotion.model';

@Injectable({
  providedIn: 'root'
})
export class PromotionService {
  private apiUrl = `${environment.apiUrl}/promotions`;

  constructor(private http: HttpClient) { }

  // Carousel Promotions
  getActiveCarouselPromotions(): Observable<CarouselPromotion[]> {
    return this.http.get<CarouselPromotion[]>(
      `${this.apiUrl}/carousel-promotions/active/`
    );
  }

  getAllCarouselPromotions(activeOnly: boolean = false): Observable<CarouselPromotion[]> {
    const params = activeOnly ? { active_only: 'true' } : {};
    return this.http.get<CarouselPromotion[]>(
      `${this.apiUrl}/carousel-promotions/`,
      { params }
    );
  }

  getCarouselPromotion(id: number): Observable<CarouselPromotion> {
    return this.http.get<CarouselPromotion>(
      `${this.apiUrl}/carousel-promotions/${id}/`
    );
  }

  // Product Promotions
  getActiveProductPromotions(): Observable<ProductPromotion[]> {
    return this.http.get<ProductPromotion[]>(
      `${this.apiUrl}/product-promotions/active/`
    );
  }

  getAllProductPromotions(activeOnly: boolean = false): Observable<ProductPromotion[]> {
    const params = activeOnly ? { active_only: 'true' } : {};
    return this.http.get<ProductPromotion[]>(
      `${this.apiUrl}/product-promotions/`,
      { params }
    );
  }

  getProductPromotion(id: number): Observable<ProductPromotion> {
    return this.http.get<ProductPromotion>(
      `${this.apiUrl}/product-promotions/${id}/`
    );
  }
}
```

## Carousel Component

```typescript
// components/home-carousel/home-carousel.component.ts

import { Component, OnInit } from '@angular/core';
import { PromotionService } from '../../services/promotion.service';
import { CarouselPromotion } from '../../models/promotion.model';

@Component({
  selector: 'app-home-carousel',
  templateUrl: './home-carousel.component.html',
  styleUrls: ['./home-carousel.component.scss']
})
export class HomeCarouselComponent implements OnInit {
  promotions: CarouselPromotion[] = [];
  currentSlide = 0;
  autoPlayInterval: any;
  isLoading = true;
  error: string | null = null;

  constructor(private promotionService: PromotionService) { }

  ngOnInit(): void {
    this.loadPromotions();
  }

  loadPromotions(): void {
    this.promotionService.getActiveCarouselPromotions().subscribe({
      next: (promotions) => {
        this.promotions = promotions;
        this.isLoading = false;
        if (this.promotions.length > 1) {
          this.startAutoPlay();
        }
      },
      error: (error) => {
        console.error('Error loading carousel promotions:', error);
        this.error = 'Failed to load promotions';
        this.isLoading = false;
      }
    });
  }

  startAutoPlay(): void {
    this.autoPlayInterval = setInterval(() => {
      this.nextSlide();
    }, 5000); // Change slide every 5 seconds
  }

  stopAutoPlay(): void {
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
    }
  }

  nextSlide(): void {
    this.currentSlide = (this.currentSlide + 1) % this.promotions.length;
  }

  previousSlide(): void {
    this.currentSlide = this.currentSlide === 0 
      ? this.promotions.length - 1 
      : this.currentSlide - 1;
  }

  goToSlide(index: number): void {
    this.currentSlide = index;
    this.stopAutoPlay();
    this.startAutoPlay();
  }

  onPromotionClick(promotion: CarouselPromotion): void {
    if (promotion.link_url) {
      window.location.href = promotion.link_url;
    }
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }
}
```

```html
<!-- components/home-carousel/home-carousel.component.html -->

<div class="carousel-container" *ngIf="!isLoading && promotions.length > 0">
  <div class="carousel-slides">
    <div 
      *ngFor="let promotion of promotions; let i = index" 
      class="carousel-slide"
      [class.active]="i === currentSlide"
      [style.background-image]="'url(' + promotion.image + ')'"
      (click)="onPromotionClick(promotion)">
      
      <div class="carousel-content">
        <h2 class="carousel-title">{{ promotion.title }}</h2>
        <p class="carousel-description">{{ promotion.description }}</p>
        <button 
          *ngIf="promotion.button_text && promotion.link_url" 
          class="carousel-button">
          {{ promotion.button_text }}
        </button>
      </div>
    </div>
  </div>

  <!-- Navigation Arrows -->
  <button 
    class="carousel-control prev" 
    (click)="previousSlide()"
    *ngIf="promotions.length > 1">
    ❮
  </button>
  <button 
    class="carousel-control next" 
    (click)="nextSlide()"
    *ngIf="promotions.length > 1">
    ❯
  </button>

  <!-- Dots Indicator -->
  <div class="carousel-dots" *ngIf="promotions.length > 1">
    <span 
      *ngFor="let promotion of promotions; let i = index"
      class="dot"
      [class.active]="i === currentSlide"
      (click)="goToSlide(i)">
    </span>
  </div>
</div>

<div class="loading" *ngIf="isLoading">
  Loading promotions...
</div>

<div class="error" *ngIf="error">
  {{ error }}
</div>
```

```scss
// components/home-carousel/home-carousel.component.scss

.carousel-container {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.carousel-slides {
  position: relative;
  width: 100%;
  height: 100%;
}

.carousel-slide {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s ease-in-out;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &.active {
    opacity: 1;
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3));
  }
}

.carousel-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
  max-width: 800px;
  padding: 20px;
}

.carousel-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.carousel-description {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.carousel-button {
  padding: 15px 40px;
  font-size: 1.2rem;
  font-weight: bold;
  color: white;
  background-color: #ff4444;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);

  &:hover {
    background-color: #ff6666;
    transform: translateY(-2px);
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
  }
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(255, 255, 255, 0.7);
  color: #333;
  border: none;
  font-size: 2rem;
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  z-index: 2;

  &:hover {
    background-color: rgba(255, 255, 255, 0.9);
  }

  &.prev {
    left: 20px;
    border-radius: 0 4px 4px 0;
  }

  &.next {
    right: 20px;
    border-radius: 4px 0 0 4px;
  }
}

.carousel-dots {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 2;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.7);
  }

  &.active {
    background-color: white;
  }
}

.loading,
.error {
  text-align: center;
  padding: 100px 20px;
  font-size: 1.2rem;
}

.error {
  color: #ff4444;
}
```

## Product Card Component with Promotion

```typescript
// components/product-card/product-card.component.ts

import { Component, Input } from '@angular/core';
import { Product } from '../../models/promotion.model';

@Component({
  selector: 'app-product-card',
  templateUrl: './product-card.component.html',
  styleUrls: ['./product-card.component.scss']
})
export class ProductCardComponent {
  @Input() product!: Product;

  get mainImage(): string {
    return this.product.images && this.product.images.length > 0
      ? this.product.images[0].image
      : 'assets/placeholder-product.png';
  }

  get savings(): number {
    if (this.product.has_promotion && this.product.promotional_price) {
      return this.product.price - this.product.promotional_price;
    }
    return 0;
  }
}
```

```html
<!-- components/product-card/product-card.component.html -->

<div class="product-card" [routerLink]="['/products', product.id]">
  <!-- Promotion Badge -->
  <div 
    *ngIf="product.has_promotion && product.active_promotion" 
    class="promotion-badge"
    [style.background-color]="product.active_promotion.badge_color">
    {{ product.active_promotion.badge_text }}
  </div>

  <!-- Product Image -->
  <div class="product-image">
    <img [src]="mainImage" [alt]="product.name">
  </div>

  <!-- Product Info -->
  <div class="product-info">
    <h3 class="product-name">{{ product.name }}</h3>
    
    <!-- Price Section -->
    <div class="price-section">
      <div class="prices">
        <span 
          class="original-price" 
          [class.strikethrough]="product.has_promotion">
          ${{ product.price | number:'1.2-2' }}
        </span>
        <span 
          *ngIf="product.has_promotion && product.promotional_price" 
          class="promotional-price">
          ${{ product.promotional_price | number:'1.2-2' }}
        </span>
      </div>
      
      <div 
        *ngIf="product.has_promotion && product.discount_percentage" 
        class="savings">
        Save {{ product.discount_percentage | number:'1.0-0' }}%!
      </div>
    </div>

    <!-- Stock Status -->
    <div class="stock-status">
      <span *ngIf="product.stock_quantity > 0" class="in-stock">
        In Stock
      </span>
      <span *ngIf="product.stock_quantity === 0" class="out-of-stock">
        Out of Stock
      </span>
    </div>
  </div>
</div>
```

```scss
// components/product-card/product-card.component.scss

.product-card {
  position: relative;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  background: white;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
}

.promotion-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 12px;
  color: white;
  font-weight: bold;
  font-size: 0.85rem;
  border-radius: 4px;
  z-index: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.product-image {
  width: 100%;
  height: 250px;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  &:hover img {
    transform: scale(1.1);
  }
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 1.1rem;
  margin-bottom: 10px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-section {
  margin-bottom: 10px;
}

.prices {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.original-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;

  &.strikethrough {
    text-decoration: line-through;
    color: #999;
    font-size: 1rem;
    font-weight: normal;
  }
}

.promotional-price {
  font-size: 1.3rem;
  font-weight: bold;
  color: #ff4444;
}

.savings {
  font-size: 0.9rem;
  color: #00aa00;
  font-weight: bold;
}

.stock-status {
  .in-stock {
    color: #00aa00;
    font-size: 0.9rem;
  }

  .out-of-stock {
    color: #ff4444;
    font-size: 0.9rem;
  }
}
```

## Usage in Home Component

```typescript
// pages/home/home.component.ts

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  template: `
    <div class="home-page">
      <!-- Carousel with promotions -->
      <app-home-carousel></app-home-carousel>
      
      <!-- Other home page content -->
      <section class="featured-products">
        <h2>Featured Products</h2>
        <div class="product-grid">
          <app-product-card 
            *ngFor="let product of products" 
            [product]="product">
          </app-product-card>
        </div>
      </section>
    </div>
  `,
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  products: Product[] = [];

  constructor(private productService: ProductService) { }

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        this.products = products;
      },
      error: (error) => {
        console.error('Error loading products:', error);
      }
    });
  }
}
```

## Environment Configuration

```typescript
// environments/environment.ts

export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};

// environments/environment.prod.ts

export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api'
};
```

This completes the frontend integration! The components are ready to use with your Django backend.
