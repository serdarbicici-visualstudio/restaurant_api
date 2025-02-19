# Restaurant Management API Documentation

**Authors:**  
- Muhammed Furkan Ataç - 150210304  
- Ömer Erdağ - 150210332  
- Serdar Biçici - 150210331  
- Batuhan Sal - 150210316  

**Date:** January 6, 2025  

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Data Model and Documentation](#data-model-and-documentation)  
   - [Tables](#tables)  
   - [Customer](#customer)  
   - [Reservation](#reservation)  
   - [Menu](#menu)  
   - [Order](#order)  
   - [Order Item](#order-item)  
   - [Staff](#staff)  
   - [Payment](#payment)  
3. [ER Diagram](#er-diagram)  
4. [Relationships Between Tables](#relationships-between-tables)  
   - [Customers and Reservations](#customers-and-reservations)  
   - [Tables and Reservations](#tables-and-reservations)  
   - [Reservations and Orders](#reservations-and-orders)  
   - [Orders and Order Items](#orders-and-order-items)  
   - [Menu and Order Items](#menu-and-order-items)  
   - [Orders and Payments](#orders-and-payments)  
5. [Complex Queries](#complex-queries)  
   - [Customer Spending Query](#customer-spending-query)  
   - [Popular Dishes Query](#popular-dishes-query)  
   - [Pending Orders Query](#pending-orders-query)  
   - [Customers Who Spent Above Average](#customers-who-spent-above-average)  
6. [CRUD Operations and Implementations](#crud-operations-and-implementations)  
   - [Analytics Endpoints](#analytics-endpoints)  
   - [Customers Endpoints](#customers-endpoints)  
   - [Menu Endpoints](#menu-endpoints)  
   - [Order Items Endpoints](#order-items-endpoints)  
   - [Orders Endpoints](#orders-endpoints)  
   - [Payments Endpoints](#payments-endpoints)  
   - [Staff Endpoints](#staff-endpoints)  
   - [Tables Endpoints](#tables-endpoints)  
7. [Challenges and Solutions](#challenges-and-solutions)  

---

## Project Overview

The **Restaurant Management API** is a web-based system designed to streamline restaurant operations. It enables efficient management of customers, reservations, menu items, orders, payments, and staff information.  

**Key features of the API include:**  
- Managing customer details and contact information.  
- Handling table reservations with time constraints to prevent double bookings.  
- Maintaining a dynamic menu with categories and pricing.  
- Tracking orders and associated items for reservations.  
- Recording payment transactions and supporting multiple payment methods.  
- Managing staff roles and work shifts.  

The API supports **CRUD operations** and integrates **JWT-based authentication** for secure access. It also includes **analytical features and complex queries** to generate reports, such as revenue tracking and pending orders. **Swagger documentation** is provided to ensure ease of testing and integration.  

---

## Data Model and Documentation

### Tables
Stores information about the restaurant tables.  
- **Primary Key:** `table_id` (NOT NULL)  
- **Attributes:**  
  - `capacity` (INT)  
  - `location` (VARCHAR(50))  

### Customer
Stores customer information.  
- **Primary Key:** `customer_id` (NOT NULL)  
- **Attributes:**  
  - `name` (VARCHAR(100))  
  - `contact_details` (VARCHAR(100), UNIQUE)  

### Reservation
Tracks reservations linking customers to tables.  
- **Primary Key:** `reservation_id` (NOT NULL)  
- **Attributes:**  
  - **Foreign Keys:** `customer_id` (FK to Customers, NOT NULL), `table_id` (FK to Tables, NOT NULL)  
  - `reservation_date` (DATE)  
  - `reservation_time` (TIME)  
  - `status` (ENUM)  

### Menu
Maintains a catalog of dishes.  
- **Primary Key:** `dish_id` (NOT NULL)  
- **Attributes:**  
  - `dish_name` (VARCHAR(100), NOT NULL)  
  - `category` (ENUM)  
  - `price` (DECIMAL(10,2))  

### Order
Links reservations to order details.  
- **Primary Key:** `order_id` (NOT NULL)  
- **Attributes:**  
  - **Foreign Key:** `reservation_id` (FK to Reservations, NOT NULL)  
  - `total_amount` (DECIMAL(10,2))  
  - `order_status` (ENUM)  

### Order Item
Tracks individual items in an order.  
- **Primary Key:** `order_item_id` (NOT NULL)  
- **Attributes:**  
  - **Foreign Keys:** `order_id` (FK to Orders, NOT NULL), `dish_id` (FK to Menu, NOT NULL)  
  - `quantity` (INT)  

### Staff
Stores staff details.  
- **Primary Key:** `staff_id` (NOT NULL)  
- **Attributes:**  
  - `name` (VARCHAR(100), NOT NULL)  
  - `role` (ENUM)  
  - `shift` (ENUM)  

### Payment
Tracks payment transactions.  
- **Primary Key:** `payment_id` (NOT NULL)  
- **Attributes:**  
  - **Foreign Key:** `order_id` (FK to Orders, NOT NULL)  
  - `amount_paid` (DECIMAL(10,2))  
  - `payment_method` (ENUM)  
  - `payment_date` (TIMESTAMP)  

---

## Relationships Between Tables

### Customers and Reservations
- **Type:** One-to-Many  
- **Each reservation is linked to a single customer.**  

### Tables and Reservations
- **Type:** One-to-Many  
- **Each reservation is linked to a single table.**  

### Reservations and Orders
- **Type:** One-to-Many  
- **Each reservation can have multiple orders.**  

### Orders and Order Items
- **Type:** One-to-Many  
- **Each order can have multiple order items.**  

### Menu and Order Items
- **Type:** One-to-Many  
- **Each order item corresponds to one menu item.**  

### Orders and Payments
- **Type:** One-to-Many  
- **Each order can have multiple payments.**  

---

## Complex Queries

### Customer Spending Query
```sql
SELECT c.name AS customer_name, SUM(o.total_amount) AS total_spent
FROM Customers c
JOIN Reservations r ON c.customer_id = r.customer_id
JOIN Orders o ON r.reservation_id = o.reservation_id
GROUP BY c.customer_id
ORDER BY total_spent DESC;
