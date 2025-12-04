from mongoengine import Document, StringField, DecimalField, DictField

class Product(Document):
    title = StringField(required=True)
    price = DecimalField()  
    link = StringField(unique=True) 
    description = StringField()
    image_url = StringField()
    status = StringField() 
    store = StringField(default="TexnoSmart")
    
    specs = DictField() 

    article = StringField(unique=True, sparse=True)

    meta = {
        'collection': 'products',
        'indexes': ['link', 'article']
    }

    def __str__(self):
        return self.title