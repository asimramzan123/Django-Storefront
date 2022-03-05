from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist 
from store.models import Collection, Customer, Product, OrderItem, Order
from django.db.models import Q, F, Value, Func, Count, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Max, Min, Sum, Count, Avg

from django.contrib.contenttypes.models import ContentType
from store.models import Product
from tags.models import TaggedItem


def hello(request):
    # managers in query set
    query_set = Product.objects.all()

    # adding try exceptions incase id is not locatable like pk = 0
    try:
        product = Product.objects.get(pk = 1)   #product with id 1
    except ObjectDoesNotExist:
        pass # nothing to show now :)
    query_set.filter().filter().order_by()#chaining the query and at some point that query would be evaluated.

    # better way to use filter() then try except block
    product = Product.objects.filter(pk = 1).first()  #product with id 1, right away calling first method of query set.
    
    # one way, gen SQL in DB
    for product in query_set:
        print(product)

    # other scenerio  using list
    list(query_set)

    # getting individual elements with slicing like picking 1st 4 elements
    query_set[0:4]


    # using filter in query set`
    query_set = Product.objects.filter(unit_price__gt = 20) #unit_price__gt is queryset api field text(keyword = value)
    
    # product : inventory <20, price >20
    # products_w_mkw = Product.objects.filter(inventory__lt = 20, unit_price__lt =20) # inventory and price <20(combine with AND keyword) 
    products_w_1kw = Product.objects.filter(inventory__lt = 20).filter(unit_price__lt =20) # inventory and price <20 but with diff filter method. 
    

    # using query Q for OR operation in DB, lets import this first...,,, 
    # | converts into SQL OR operation.. Can use & for AND operation but better to use without Q object.
    productsq_w_Q = Product.objects.filter(Q(inventory_lt =20) | Q(unit_price_lt = 20))
    productsq_w_nQ = Product.objects.filter(Q(inventory_lt =20) | ~Q(unit_price_lt = 20))# not operator ~


    # getting price and inventory fields with comparison, Using F object(comparing Fields by F:)
    # F object create WHERE class in SQL. Can get fields in related table. like inventory of a product with id of it's collection.
    productsq_w_F = Product.objects.filter(inventory = F("unit_price"))
    productsq_wF_fcoll = Product.objects.filter(inventory = F("collectoin__id"))


    # Sorting
    products_sort_asc = Product.objects.order_by('title') # sort in ASC
    products_sort_dsc = Product.objects.order_by('-title') # sort in DSC
    products_sort_fields_by_order = Product.objects.order_by('unit_price','-title') # sort in DSC but price wise
    products_sortf_inrev_order = Product.objects.order_by('unit_price','-title').reverse() # sort in DSC but price wise and in reverse title order
    product = Product.objects.order_by('title')[0]# first product(while render pass single product instead list)
    product = Product.objects.earliest('title')# sort all products in ASC and return first objects
    product = Product.objects.latest('title')# sort all products in DSC and return first objects

        # Limiting results
    # returning limited no of objects in this array, using slicing...
    # let say getting first 5 index products, at 0,1,2,3,4 indices
    products = Product.objects.all()[:5] #slicing convert into LIMIT in SQL.
    products = Product.objects.all()[5:15] #LIMIT and OFFSET of 10 for skipping.

    # selecting fields for query
    # using query to get some subset of data, like id and title from data.
    products = Product.objects.values('id', 'title')

    # reading related fields gets Inner Join(between products and collection),we get dictionery objects instead product instance.
    products = Product.objects.values('id', 'title', 'collection__title')
    products = Product.objects.values_list('id', 'title', 'collection__title') #we get a bunch of tuples

    # products_ord = Product.objects.values('id', 'title').values('title')
    query_res = Product.objects.values('product_id').distinct() # selecting distinct prod_id's(no duplicates) from OrderItem table.
    # Now getting all above distinct id's.
    query_res = Product.objects.filter(id__in = OrderItem.objects.values('product_id').distinct()).orderby('title') # filtered data fetching using id__in

    # selecting related queries
    # using products = Product.objects.all(), gets you same no of quiries as no of data, so it slows down the results. It queries product tables.
    products = Product.objects.select_related('collection').all() # first select related then shows data.

    # to preload the promotion field from product class, we use prefetch_related method, gen join b/w promotion and products.
    query_set = Product.objects.prefetch_related('promtions').all()
    # all products with both promotion and collection, order dont matter    
    query_set = Product.objects.prefetch_related('promtions').select_related('collection').all()

    # getting last 5 items with customer and items
    # product = Product.objects.prefetch_related('customer__id').select_related('order__id').latest('title')[:5]
    product = Order.objects.select_related('customer').order_by('-placed_at')[:5]
    # using django reverse relationship(orderitem_set) for items by order class to prefetch_related data.
    product = Order.objects.select_related('customer').prefetch_related('orderitem_set').order_by('-placed_at')[:5]
    # loading product reference in each order item
    product = Order.objects.select_related('customer').prefetch_related('orderitem_set__product ').order_by('-placed_at')[:5]
    
    # Aggregating Objects
    results = product.objects.aggregate(count = Count('id'), min_price = Min('unit_price')) # total no of products by id, descrition, unit_price. returns dict
    results = product.objects.filter(collection__id = 1).aggregate(count = Count('id'), min_price = Min('unit_price')) # can filter out the collection items
   
    # Annotating objects
    # adding additional attrib to objects while querying them, use annotating objects
    query_set_annot = Customer.objects.annotate(is_new = Value(True))  # can't use bool directly, but use Value object to pass bool
    query_set_annot = Customer.objects.annotate(new_id = F('id') + 1)  #referencing another fields into this model + 1 to gen new id

    # Database Func
    # calling concat func for concatinating strings, concat first_name with space and last name
    query_set_func = Customer.objects.annotate(
        full_name = Func(F('first_name'), Value(' '), F('last_name'), function = 'CONCAT')
    )

    # shorter way to concate first and last name
    query_set_concat = Concat('first_name', Value('' ), 'last_name')

    # Grouping data
    query_set_group = Customer.objects.annotate(
        orders_count = Count('order')  # auto creates order field, counting num of orders using left outer join
    )

    #Expression Wrapper object, takes unit price and * it 0.8
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(discounted_price = discounted_price)

    # return render(request, 'hello.html',{'name':'Asim', 'Products':list(query_set)}) # change it accordingly :)
    # return render(request, 'hello.html',{'name':'Asim', 'orders':list(query_set)}) #to display first 5 orders
    return render(request, 'hello.html',{'name':'Asim', 'result':results}) 



def say_hello(request):
    # obj attr returns manager object which is gateway to db.
    # Tagged App is decoupled from store app
    content_type = ContentType.objects.get_for_models(Product) # rep content type table in DB

    #return TaggedItem objects, # preload tag field(select_related('tag'))
    query_st = TaggedItem.objects\
        .select_related('tag').filter(      
        content_type = content_type, object_id = 1
    )

    # Better way using Custom Managers
    TaggedItem.objects.get_tags_for(Product, 1)

    # getting data from db is going to store data into memory called query_cache
    # cache mechanism built into query set, 
    query_set = Product.objects.all()
    list(query_set) # reading obj from disk is always slower than reading from memory.
    list(query_set) # second time django would read it from query_set cache
    query_set[0]    # gets data fron cache

    # Creating objects
    collection = Collection()
    collection.title = 'Video Game'
    collection.featured_products = Product(pk = 1)
    collection.save()

    # short hand in single line :), better to use above traditional approach
    collection = Collection.objects.create(name = 'Video Games', featured_product_id = 1)

    # Updating Object
    # To properly update an object, first retrieve it from DB then update it
    collection = Collection.objects.get(pk = 12)
    collection.featured_products = None
    collection.objects.filter(pk = 11).update(featured_product = None)

    # Deleting Objects
    # can del single or multiple objects in a query set
    collection.delete() #to del single
    Collection.objects.filter(id__gt = 5).delete()

    # return render(request, 'hello.html', {'name': 'Asim','tags':list(query_st)})
    return render(request, 'hello.html', {'name': 'Asim'})
