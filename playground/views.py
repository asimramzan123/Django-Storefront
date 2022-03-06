from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist 
from store.models import Collection, Customer, Product, OrderItem, Order
from django.db.models import Q, F, Value, Func, Count, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Max, Min, Sum, Count, Avg
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType

from store.models import Product
from tags.models import TaggedItem


def hello(request):

    """ adding try exceptions incase id is not locatable like pk = 0.
        product with id 1(Product.objects.get(pk = 1)).
        adding Pass in except as nothing to show now :), to prevent error.
        chaining the query and at some point that query would be evaluated.
    """
    query_set = Product.objects.all()
    try:
        product = Product.objects.get(pk = 1)   
    except ObjectDoesNotExist:
        pass
    query_set.filter().filter().order_by()


    """ Its better to use filter() then try except block.
        product with id 1, right away calling first method of query set.
    """
    product = Product.objects.filter(pk = 1).first() 
    
    
    """ Generating SQL in DB:
        other scenerio  using list.
        getting individual elements with slicing like picking 1st 4 elements.
    """
    for product in query_set:
        print(product)
    list(query_set)
    query_set[0:4]


    """ --> Using filter in query set:
        unit_price__gt is queryset api field text(keyword = value).
        product : inventory <20, price >20
        products_w_mkw = Product.objects.filter(inventory__lt = 20, unit_price__lt =20) # inventory and price <20(combine with AND keyword) 
    """
    query_set = Product.objects.filter(unit_price__gt = 20) 
    products_w_1kw = Product.objects.filter(inventory__lt = 20).filter(unit_price__lt =20) # inventory and price <20 but with diff filter method. 
    

    """ --> Using query Q for OR operation in DB, lets import this first.
        | converts into SQL OR operation. Can use & for AND operation but better to use without Q object.
        not operator ~ with field.
    """
    productsq_w_Q = Product.objects.filter(Q(inventory_lt =20) | Q(unit_price_lt = 20))
    productsq_w_nQ = Product.objects.filter(Q(inventory_lt =20) | ~Q(unit_price_lt = 20))


    """ getting price and inventory fields with comparison, Using F object(comparing Fields by F:)
        F object create WHERE class in SQL. Can get fields in related table. 
        like inventory of a product with id of it's collection.
    """
    productsq_w_F = Product.objects.filter(inventory = F("unit_price"))
    productsq_wF_fcoll = Product.objects.filter(inventory = F("collectoin__id"))


    """ --> Sorting:
        sort in ASC
        sort in DSC
        sort in DSC but price wise.
        sort in DSC but price wise and in reverse title order.
        first product(while render pass single product instead list).
        sort all products in ASC and return first objects.
        sort all products in DSC and return first objects.
    """
    products_sort_asc = Product.objects.order_by('title') 
    products_sort_dsc = Product.objects.order_by('-title') 
    products_sort_fields_by_order = Product.objects.order_by('unit_price','-title') 
    products_sortf_inrev_order = Product.objects.order_by('unit_price','-title').reverse() 
    product = Product.objects.order_by('title')[0]
    product = Product.objects.earliest('title')
    product = Product.objects.latest('title')


    """ --> Limiting results:
        returning limited no of objects in this array, using slicing.
        let say getting first 5 index products, at 0,1,2,3,4 indices.
        slicing convert into LIMIT in SQL.
        LIMIT and OFFSET of 10 for skipping.
    """
    products = Product.objects.all()[:5]
    products = Product.objects.all()[5:15]


    """ --> selecting fields for query:
        using query to get some subset of data, like id and title from data.
        reading related fields gets Inner Join(between products and collection),we get dictionery objects instead product instance.
        we get a bunch of tuples.
        products_ord = Product.objects.values('id', 'title').values('title')
        selecting distinct prod_id's(no duplicates) from OrderItem table.
        Now getting all above distinct id's. Filtered data fetching using id__in
    """
    products = Product.objects.values('id', 'title')
    products = Product.objects.values('id', 'title', 'collection__title')
    products = Product.objects.values_list('id', 'title', 'collection__title') 
    query_res = Product.objects.values('product_id').distinct()
    query_res = Product.objects.filter(id__in = OrderItem.objects.values('product_id').distinct()).orderby('title') 


    """ --> selecting related queries:
        using products = Product.objects.all(), gets you same no of quiries as no of data, so it slows down the results. 
        It queries product tables.
        first select related then shows data.
        to preload the promotion field from product class, we use prefetch_related method, gen join b/w promotion and products.
        all products with both promotion and collection, order dont matter    
    """
    products = Product.objects.select_related('collection').all()
    query_set = Product.objects.prefetch_related('promtions').all()
    query_set = Product.objects.prefetch_related('promtions').select_related('collection').all()


    """ --> getting last 5 items with customer and items:
        product = Product.objects.prefetch_related('customer__id').select_related('order__id').latest('title')[:5]
        using django reverse relationship(orderitem_set) for items by order class to prefetch_related data. 
        loading product reference in each order item.
    """
    product = Order.objects.select_related('customer').order_by('-placed_at')[:5]
    product = Order.objects.select_related('customer').prefetch_related('orderitem_set').order_by('-placed_at')[:5]
    product = Order.objects.select_related('customer').prefetch_related('orderitem_set__product ').order_by('-placed_at')[:5]
    

    """ --> Aggregating Objects:
        aggregate total no of products by id, descrition, unit_price(count = Count('id'), min_price = Min('unit_price'))
        then in end returns dict.
        can filter out the collection items(filter(collection__id = 1)).
    """
    results = product.objects.aggregate(count = Count('id'), min_price = Min('unit_price'))
    results = product.objects.filter(collection__id = 1).aggregate(count = Count('id'), min_price = Min('unit_price'))
    
    
    """ --> Annotating objects:
        adding additional attrib to objects while querying them, use annotating objects.
        can't use bool directly, but use Value object to pass bool(is_new = Value(True)).
        referencing another fields into this model + 1 to gen new id(new_id = F('id') + 1)
    """
    query_set_annot = Customer.objects.annotate(is_new = Value(True)) 
    query_set_annot = Customer.objects.annotate(new_id = F('id') + 1)

    """ --> Database Func:
        calling concat func for concatinating strings, concat first_name with space and last name.
        shorter way to concate first and last name.
    """
    query_set_func = Customer.objects.annotate(
        full_name = Func(F('first_name'), Value(' '), F('last_name'), function = 'CONCAT'))
    query_set_concat = Concat('first_name', Value('' ), 'last_name')
    
    
    """ --> Grouping data:
        auto creates order field(Count('order'), counting num of orders using left outer join in DB
        Expression Wrapper object, takes unit price and * it 0.8
    """
    query_set_group = Customer.objects.annotate(
        orders_count = Count('order'))  
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(discounted_price = discounted_price)


    """ obj attr returns manager object which is gateway to db.
        Tagged App is decoupled from store app.
        return TaggedItem objects, preload tag field(select_related('tag'))
        Better way using Custom Managers(TaggedItem.objects.get_tags_for(Product, 1))
    """
    content_type = ContentType.objects.get_for_models(Product) # rep content type table in DB
    query_st = TaggedItem.objects\
        .select_related('tag').filter(      
        content_type = content_type, object_id = 1)
    TaggedItem.objects.get_tags_for(Product, 1)
    
    
    """ getting data from db is going to store data into memory called query_cache
        cache mechanism built into query set.
        list(query_set) # reading obj from disk is always slower than reading from memory.
        list(query_set) # second time django would read it from query_set cache
        query_set[0]    # gets data fron cach
    """
    query_set = Product.objects.all()
    list(query_set)
    list(query_set)
    query_set[0]   


    # Creating objects, to modify data if changed in single file.
    collection = Collection()
    collection.title = 'Video Game'
    collection.featured_products = Product(pk = 1)
    collection.save()


    # short hand in single line :), better to use above traditional(object based) approach.
    collection = Collection.objects.create(name = 'Video Games', featured_product_id = 1)


    """ --> Updating Object:
    # To properly update an object, first retrieve it from DB then update it"""
    collection = Collection.objects.get(pk = 12)
    collection.featured_products = None
    collection.objects.filter(pk = 11).update(featured_product = None)


    """ --> Deleting Objects:
    can del single(collection.delete()) or 
    multiple objects(Collection.objects.filter(id__gt = 5).delete()) in a query set"""
    collection.delete()
    Collection.objects.filter(id__gt = 5).delete()


    """ --> Transactions:
        Saving changes in atomic way, if any changes failed,all changes should be rolled back.
        save the order before we can save it's items.
        creating parent object before we create child.
        if we save order, exception comes saying DB is inconsistent state.
        getting order without an item(bad thing yeah.), so we would apply atomicity
        importing transaction module then using it's decorator function() to wrap this entire function 
        as transaction.
    """
    with transaction.atomic():
        order = order()
        order_customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

    
    """ Executing Raw SQL Queries:
        Every manager has raw method to execute simple SQL queries.
        use this raw method approach only when dealing with complex queries.
        -sometime we execute queries that don't map to our model objects, we can access db directly and bypass model layer.
        we are gonna use connection module, then create cursor object and now we can pass any SQL query no limits.
        can use insert, select, update and so on..  
        always close cursor to release allocated resources.
        using with connection.cursor() as cursor:, it creates object and it auto close the cursor at the end.
        to execute stored procedure, we use cursor.callproc('get_customers', [1, 2, 'a'])
    """
    query_set = Product.objects.raw('SELECT  id, title FROM store_product')
    cursor = connection.cursor()
    cursor.execute('')
    cursor.close()

    with connection.cursor() as cursor:
        cursor.execute('')
        cursor.callproc('get_customers', [1, 2, 'a'])


    """ --> Admin Interface:

    """   
    



    """
    # return render(request, 'hello.html',{'name':'Asim', 'Products':list(query_set)}) # change it accordingly :)
    # return render(request, 'hello.html',{'name':'Asim', 'orders':list(query_set)}) #to display first 5 orders
    # return render(request, 'hello.html',{'name':'Asim', 'result':results}) 
    # return render(request, 'hello.html', {'name': 'Asim','tags':list(query_st)})
    #return render(request, 'hello.html', {'name': 'Asim'})
    """
    return render(request, 'hello.html', {'name': 'Asim','results':list(query_set)})

