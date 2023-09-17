from datetime import datetime as dt
import json


class HTMLMeta:
    def __init__(self,title:str,type:str,desc:str,url:str,keyw:list=[],img_url:str=None,img_size:str=None,datetime:dt=None,have_video:bool=False,have_picture:bool=False,follow:bool=True):
        self.__dict__ = locals()
    
    def get_meta(self):
        data = {}
        data['follow'] = 'index, follow,' if self.follow else 'noindex, nofollow,'
        data['maxImagePreview'] = 'standard' if self.have_picture else '-1'
        data['maxVideoPreview'] = 'standard' if self.have_video else '-1'
        data['imgUrl'] = self.img_url if  self.img_url else 'none'
        data['imgX'] = self.img_size.split('*')[0] if self.img_size else 'none'
        data['imgY'] = self.img_size.split('*')[1] if self.img_size else 'none'
        data['dateTime'] = self.datetime.strftime('%Y-%m-%dT%XZ') if self.datetime else 'none'
        data['title'] = self.title
        data['desc'] = self.desc
        data['type'] = self.type
        data['url'] = self.url
        data['keyw'] = ", ".join(self.keyw)

        return data
    
    def get_schema(self,type,site,site_logo,**data):
        """
        Article :\n
            art_type -> 'BlogPosting' Or 'NewsArticle'\n
            author_type -> 'Organization' Or 'Person'\n
            author\n
        Product :\n
            price -> str\n
            rate -> of 100\n
            best_rate\n
            worst_rate\n
            rate_count\n
        Video :\n
            min\n
            sec\n
        Site :\n
            Nothing!\n
        FAQ :\n
            qa -> [(Q,A),(Q,A)]\n
        HowTo :\n
            steps -> ['','']\n
            total_time -> '5':str\n

        """
        if type == 'Article':
            res = {
                "@context": "https://schema.org",
                "@type": data['art_type'],
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": self.url
                },
                "headline": self.title,
                "description": self.desc,
                "image": self.img_url if  self.img_url else '',
                "author": {
                    "@type": data['author_type'],
                    "name": data['author']
                },  
                "publisher": {
                    "@type": 'Organization',
                    "name": site,
                    "logo": {
                    "@type": "ImageObject",
                    "url": site_logo
                    }
                },
                "datePublished": self.datetime.strftime('%Y-%m-%d') if self.datetime else '',
                "dateModified": self.datetime.strftime('%Y-%m-%d') if self.datetime else ''
                }
        elif type == 'FAQ':
            res = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [{
                    "@type": "Question",
                    "name": Q,
                    "acceptedAnswer": {
                    "@type": "Answer",
                    "text": A
                    }
                } for Q,A in data['qa']]
            }
        elif type == 'HowTo':
            res = {
                "@context": "https://schema.org/", 
                "@type": "HowTo", 
                "name": self.title,
                "description": self.desc,
                "totalTime": data['total_time'],
                "step": [{
                    "@type": "HowToStep",
                    "text": step
                } for step in data['steps']]    
            }
        elif type == 'Product':
            res = {
                "@context": "https://schema.org/", 
                "@type": "Product", 
                "name": self.title,
                "image": self.img_url if  self.img_url else '',
                "description": self.desc,
                "brand": {
                    "@type": "Brand",
                    "name": site
                },
                "offers": {
                    "@type": "Offer",
                    "url": self.url,
                    "priceCurrency": "IRR",
                    "price": data['price']
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": data['rate'],
                    "bestRating": data['best_rate'],
                    "worstRating": data['worst_rate'],
                    "ratingCount": data['rate_count']
                }
            }
        elif type == 'Video':
            res = {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": self.title,
                "description": self.desc,
                "thumbnailUrl": self.img_url if  self.img_url else '',
                "uploadDate": self.datetime.strftime('%Y-%m-%d') if self.datetime else '',
                "duration": f"PT{data['min']}M{data['sec']}S",
                "contentUrl": self.url
                }
        elif type == 'Site':
            res = {
                "@context": "https://schema.org/",
                "@type": "WebSite",
                "name": site,
                "url": self.url
            }
        else:
            res = {}
        
        return json.dumps(res, ensure_ascii=False, default=str)
    

