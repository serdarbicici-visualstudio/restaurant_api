-- Disable foreign key checks for table creation
SET FOREIGN_KEY_CHECKS = 0;

-- Create Database
CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'admin' or 'user'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create Tables Table
CREATE TABLE IF NOT EXISTS Tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    capacity INT NOT NULL CHECK (capacity > 0),
    location VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Create Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_details VARCHAR(100) UNIQUE NOT NULL
) ENGINE=InnoDB;

-- Create Reservations Table
CREATE TABLE IF NOT EXISTS Reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    table_id INT NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    person_count INT NOT NULL CHECK (person_count > 0),
    status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES Tables(table_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create Menu Table
CREATE TABLE IF NOT EXISTS Menu (
    dish_id INT AUTO_INCREMENT PRIMARY KEY,
    dish_name VARCHAR(100) NOT NULL,
    category ENUM('Appetizer', 'Main Course', 'Dessert', 'Beverage') NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0)
) ENGINE=InnoDB;

-- Create Orders Table
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    order_status ENUM('Pending', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (reservation_id) REFERENCES Reservations(reservation_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create Order_Items Table
CREATE TABLE IF NOT EXISTS Order_Items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    dish_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (dish_id) REFERENCES Menu(dish_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create Staff Table
CREATE TABLE IF NOT EXISTS Staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role ENUM('Waiter', 'Chef', 'Manager', 'Host') NOT NULL,
    shift ENUM('Morning', 'Afternoon', 'Evening') NOT NULL
) ENGINE=InnoDB;

-- Create Payments Table
CREATE TABLE IF NOT EXISTS Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL CHECK (amount_paid >= 0),
    payment_method ENUM('Cash', 'Credit Card', 'Mobile Payment') NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Additional Constraints
-- Ensure a table can only be reserved once for the same time slot.
ALTER TABLE Reservations 
ADD CONSTRAINT unique_table_time UNIQUE (table_id, reservation_date, reservation_time);

-- Ensure unique dishes in an order
ALTER TABLE Order_Items 
ADD CONSTRAINT unique_order_menu UNIQUE (order_id, dish_id);

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
