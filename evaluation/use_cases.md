### **RESERVATION SYSTEM**



***UC1 – Manage Entities (Users and Rooms)***



**Goal in Context**: Create and manage users and rooms while ensuring system consistency and uniqueness.



**Scope \& Level**: Reservation System, user-goal



**Actors**:

* *Primary*: System / Admin



**Preconditions:**

* System is initialized
* No assumptions about existing users or rooms



**Postconditions:**

* Users and rooms reflect all valid operations
* No duplicates exist
* Related reservations are removed when entities are deleted
* System remains consistent after any sequence of entity operations



**Main Success Scenario:**

1. Actor creates a user or a room

2\. System stores the entity

3\. Actor deletes a user or a room

4\. System removes the entity



**Extensions:**

*Duplicates:*

* 1a. Entity already exists

&#x09;→ System ignores the request



*Deletion behavior:*

* 3a. Deleted user has reservations

&#x09;→ System removes all associated reservations

* 3b. Deleted room has reservations

&#x09;→ System removes all associated reservations

* 3c. Actor deletes non-existing entity

&#x09;→ System does nothing



*Complex flows:*

* 4a. Multiple users and rooms created and deleted in sequence
* 4b. Repeated create/delete operations





***UC2 – Manage Reservations***



**Goal in Context**: Allow users to create and cancel reservations while enforcing constraints such as availability and time conflicts.



**Scope \& Level:** Reservation System, user-goal



**Actors:**

* *Primary*: User
* *Secondary*: System



**Preconditions:**

* Users and rooms may exist in the system



**Postconditions:**

* Reservations reflect valid operations
* No conflicting reservations exist
* System state remains consistent



**Main Success Scenario:**

1. Actor selects a user and a room

2\. Actor requests a reservation

3\. System verifies:

* user exists
* room exists
* room is available

4\. System creates the reservation

5\. Actor cancels a reservation

6\. System removes the reservation



**Extensions:**

*Invalid references:*

* 3a. User does not exist

&#x09;→ Request ignored

* 3b. Room does not exist

&#x09;→ Request ignored



*Conflicts:*

* 3c. Room already reserved

&#x09;→ Request rejected

* 3d. Duplicate reservation

&#x09;→ Only one instance is stored



*Cancellation:*

* 5a. Reservation does not exist

&#x09;→ No effect

* 5b. Reservation already cancelled

&#x09;→ No effect



*Time constraints:*

* 3e. Time intervals overlap

&#x09;→ Reservation rejected

* 3f. Time intervals do not overlap

&#x09;→ Reservation accepted



*Invalid operations:*

* 2a. Reservation without user or room

&#x09;→ Ignored

* 2b. Operation on deleted user or room

&#x09;→ Ignored



*Concurrency-like situations:*

* 3g. Multiple users attempt to reserve the same room

&#x09;→ First valid request succeeds

* 3h. Subsequent conflicting requests are rejected



*Complex flows:*

* 4a. One user creates reservations for multiple rooms
* 4b. Multiple users create reservations across rooms
* 4c. Mixed sequences of create, cancel, and re-create
* 4d. Repeated reservation attempts







### **E-shop system**



***UC1 – Manage Users and Products***



**Goal in Context**: Create and manage users and products while ensuring correct handling of duplicates, updates and system consistency.



**Scope \& Level**: E-shop system, user-goal



**Actors**:

* *Primary*: System / Admin



**Preconditions:**

* System is initialized



**Postconditions:**

* Users and products reflect all valid operations
* No duplicate users exist
* Product stock is correctly accumulated
* Product price reflects the latest update
* System remains consistent after deletions



**Main Success Scenario:**

1. Actor creates a user
2. System stores the user
3. Actor adds a product
4. System stores the product with price and stock
5. Actor updates an existing product
6. System increases stock and updates price
7. Actor deletes a user or product
8. System removes the entity



**Extensions:**

*Duplicates:*

* 1a. User already exists  
→ System ignores the request
* 3a. Product already exists  
→ Stock is increased and price updated



*Invalid values:*

* 3b. Product created with negative stock  
→ Operation ignored



*Deletion:*

* 7a. Deleting non-existing user or product  
→ No effect
* 7b. Deleting user with cart  
→ Cart is removed
* 7c. Deleting user with orders  
→ Orders remain unchanged
* 7d. Deleting product  
→ Product removed from catalog and stock only
→ Existing carts and orders are not modified

&#x09;

*Consistency and repeated operations:*

* 8a. Repeated create/update/delete operations
* 8b. Interleaved product updates





***UC2 – Manage Shopping Cart***



**Goal in Context**: Allow users to manage their shopping cart while respecting stock constraints and ensuring valid operations.



**Scope \& Level**: E-shop system, user-goal



**Actors**:

* *Primary*: User
* *Secondary*: System



**Preconditions:**

* User and products may exist in the system



**Postconditions:**

* Cart reflects valid operations
* Quantities are valid and do not exceed stock
* Carts of different users are independent



**Main Success Scenario:**

1. Actor adds a product to cart
2. System verifies:

   * user exists
   * product exists
   * quantity is valid
   * quantity ≤ available stock
3. System adds or updates item in cart
4. Actor removes product from cart
5. System updates cart accordingly



**Extensions:**

*Invalid references:*

* 2a. User does not exist  
→ Operation ignored
* 2b. Product does not exist  
→ Operation ignored



*Invalid quantity:*

* 2c. Quantity is zero or negative  
→ Operation ignored
* 2d. Quantity exceeds stock  
→ Operation rejected



*Cart behavior:*

* 3a. Same product added multiple times  
→ Quantities are accumulated
* 3b. Cart may contain products that no longer exist in the system.
* 4a. Removing non-existing item  
→ No effect
* 4b. Removing from empty cart  
→ No effect



*Isolation and concurrency:*

* 3c. Multiple users modify carts  
→ Carts remain independent
* 3d. Multiple users add same product concurrently  
→ Stock constraints enforced



*Complex flows:*

* 4c. Repeated add/remove operations
* 4d. Mixed cart updates before checkout





***UC3 – Checkout and Order Processing***



**Goal in Context**: Process user orders while ensuring stock consistency, atomicity and correct order creation.



**Scope \& Level**: E-shop system, user-goal



**Actors**:

* *Primary*: User
* *Secondary*: System



**Preconditions:**

* User exists
* Cart may contain items



**Postconditions:**

* Successful checkout creates an order
* Stock is reduced accordingly
* Cart is cleared
* Failed checkout does not change system state



**Main Success Scenario:**

1. Actor initiates checkout
2. System verifies:

   * user exists
   * cart is not empty
   * all products are available in required quantities
3. System calculates total price based on current product prices (prices at checkout time)
4. System reduces stock
5. System creates order
6. System clears cart



**Extensions:**

*Invalid conditions:*

* 2a. User does not exist  
→ Operation ignored
* 2b. Cart is empty  
→ Checkout fails
* 2c. Product no longer exists  
→ Checkout fails
* 2d. Insufficient stock  
→ Checkout fails



*Atomicity:*

* 4a. Any validation fails  
→ No changes applied



*Concurrency-like situations:*

* 2e. Multiple users checkout same product  
→ First succeeds, others may fail



*Post-deletion cases:*

* 2f. Checkout after user deletion  
→ Operation ignored
* 2g. Checkout after product deletion  
→ Cart remains unchanged, checkout fails



*Complex flows:*

* 6a. Multiple users performing checkout
* 6b. Interleaved checkout and cart updates
* 6c. Large sequence of operations



