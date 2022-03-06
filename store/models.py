from django.db import models


class Collection(models.Model):
    title = models.CharField(max_length = 255)
    featured_products = models.ForeignKey("Product",
     on_delete=models.SET_NULL, null=True, related_name= '+')#'Product' resolve circular dependency
    
    def __str__(self) -> str:
        return self.title

    # default sorting of collection objects, ordering list of fields
    class Meta:
        ordering = ['title']


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)# this provoke django to automatically cread id for us.
    title = models.CharField(max_length=50)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits = 6, decimal_places = 2) # always use this for numeric values
    slug = models.SlugField()# so search engines could fine our product.
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now = True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)# accidently deleting collection should't delete product.
    promotions =models.ManyToManyField(Promotion)

    # def __str__(self) -> str:
    #     return self.title

    # # default sorting of collection objects, ordering list of fields
    # class Meta:
    #     ordering = ['title']

class Customer(models.Model):
    # if any changes comes, you need to change once here.
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_SILVER = 'S'

    MEMBERSHIP = [
        # MEMBERSHIP_BRONZE for DB, 'Bronze' for human readable names in admin interface.
        (MEMBERSHIP_BRONZE, 'Bronze'), 
        (MEMBERSHIP_GOLD, 'Gold'),
        (MEMBERSHIP_SILVER, 'Silver'),
    ]

    first_name =models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique = True)
    phone_number = models.CharField(max_length= 255)
    birthdate = models.DateField(null = True, blank = True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP, default=MEMBERSHIP_BRONZE) # best practice is to define this values separately.
    
    class Meta:
        db_table = 'store_customers'
        indexes = [
            # list of indexes
            models.Index(fields=['last_name', 'first_name'])
        ]


class Order(models.Model):
    PENDING = 'P'
    COMPLETE = 'C'
    FAILED = 'F'

    PAYMENT_STATUS = [
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add = True) #django automatically populated this choices
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS, default=PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)# deleting customer should never delete order from DB as it represent our sales record.


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()   #prevent -ve values to store in this field.
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)# we should always store price of product by the time it was ordered.


class Address(models.Model):
    street = models.CharField(max_length=254)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key = True) 
    zip = models.PositiveIntegerField(null = True)
    """ one to one relationship between 2 modules(Customer,Address), customer should exists before we create an address.
    without setting this django gen id, which have onetomany relationship. 
    on_delete models.CASCADE, is when we delete a customer an associated address should auto deleted
    on_delete=models.PROTECT, is when we can't delete a parent untill child is deleted.
    on_delete=models.DEFAULT, is when we set values to their defaults states."""
        

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class Cart_Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)#delete a cart it would delete Cart_Items automatically
    product = models.ForeignKey(Product, on_delete=models.CASCADE)# if product never ordered, should be removed from existing shopping carts as well.
    quantitiy = models.PositiveSmallIntegerField()
