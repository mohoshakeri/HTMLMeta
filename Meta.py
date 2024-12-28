import json
import re
from datetime import datetime, timedelta

from PIL import Image
from bs4 import BeautifulSoup
from django.core.handlers.wsgi import WSGIRequest
from django.http import *
from django.shortcuts import render
from django.views.generic import *

SITE = "x"
DOMAIN = "x.com"
IMAGE_PATH = "static/img/01.png"
IMAGE_SIZE = "841*546"
LOGO_PATH = "static/img/logo.png"


def error_response(request: WSGIRequest, status: int, data=dict()):
    if data is None:
        data = {}
    match status:
        case 404:
            return HttpResponseNotFound(render(request, "404.html", context=data))
        case 403:
            return HttpResponseForbidden(render(request, "403.html", context=data))


class MetaView(View):
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

    title = ""
    desc = ""
    keyw = []
    img_url = f"https://{DOMAIN}/{IMAGE_PATH}"
    img_size = IMAGE_SIZE
    datetime = None
    have_video = False
    have_picture = False
    follow = True
    schema_kwargs = {
        "type": "Site",
        "site": SITE,
        "site_logo": f"https://{DOMAIN}/{LOGO_PATH}",
    }
    page_type = "Website"
    publish_datetime = None

    def generate_meta(self):
        data = {}
        data["follow"] = "index, follow," if self.follow else "noindex, nofollow,"
        data["maxImagePreview"] = "standard" if self.have_picture else "-1"
        data["maxVideoPreview"] = "standard" if self.have_video else "-1"
        data["imgUrl"] = self.img_url if self.img_url else "none"
        data["imgX"] = self.img_size.split("*")[0] if self.img_size else "none"
        data["imgY"] = self.img_size.split("*")[1]
        data["dateTime"] = (
            self.datetime.strftime("%Y-%m-%dT%XZ") if self.datetime else "none"
        )
        data["publishedDatetime"] = (
            (
                (
                    self.publish_datetime.strftime("%Y-%m-%dT%XZ")
                    if self.publish_datetime
                    else None
                )
                or (self.datetime.strftime("%Y-%m-%dT%XZ") if self.datetime else None)
            )
            if (self.publish_datetime or self.datetime)
            else "none"
        )
        data["title"] = self.title
        data["desc"] = self.desc
        data["type"] = self.page_type
        self.url = self.request.build_absolute_uri()
        data["url"] = self.url
        data["keyw"] = ", ".join(self.keyw)

        self.meta_data = data

    def get_schema(self, **data):
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
        type = data["type"]
        site = data["site"]
        site_logo = data["site_logo"]

        if type == "Article":
            res = {
                "@context": "https://schema.org",
                "@type": data["art_type"],
                "mainEntityOfPage": {"@type": "WebPage", "@id": self.url},
                "headline": self.title,
                "description": self.desc,
                "image": self.img_url if self.img_url else "",
                "author": {"@type": data["author_type"], "name": data["author"]},
                "publisher": {
                    "@type": "Organization",
                    "name": site,
                    "logo": {"@type": "ImageObject", "url": site_logo},
                },
                "datePublished": (
                    (
                        (
                            (
                                self.publish_datetime.strftime("%Y-%m-%dT%XZ")
                                if self.publish_datetime
                                else None
                            )
                            or (
                                self.datetime.strftime("%Y-%m-%dT%XZ")
                                if self.datetime
                                else None
                            )
                        )
                        if (self.publish_datetime or self.datetime)
                        else ""
                    )
                ),
                "dateModified": (
                    self.datetime.strftime("%Y-%m-%d") if self.datetime else ""
                ),
            }
        elif type == "FAQ":
            res = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": Q,
                        "acceptedAnswer": {"@type": "Answer", "text": A},
                    }
                    for Q, A in data["qa"]
                ],
            }
        elif type == "HowTo":
            res = {
                "@context": "https://schema.org/",
                "@type": "HowTo",
                "name": self.title,
                "description": self.desc,
                "totalTime": data["total_time"],
                "step": [
                    {"@type": "HowToStep", "text": step} for step in data["steps"]
                ],
            }
        elif type == "Product":
            res = {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": self.title,
                "image": self.img_url if self.img_url else "",
                "description": self.desc,
                "brand": {"@type": "Brand", "name": site},
                "offers": {
                    "@type": "Offer",
                    "url": self.url,
                    "priceCurrency": "IRR",
                    "price": data["price"],
                    "priceValidUntil": (datetime.now() + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "availability": "https://schema.org/OnlineOnly",
                    "itemCondition": "https://schema.org/UsedCondition",
                    "hasMerchantReturnPolicy": {
                        "@type": "MerchantReturnPolicy",
                        "returnPolicyCategory": "https://schema.org/NoReturnRefund",
                        "merchantReturnDays": 0,
                    },
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingRate": {
                            "@type": "MonetaryAmount",
                            "value": "0",
                            "currency": "IRR",
                        },
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 0,
                                "maxValue": 0,
                                "unitCode": "h",
                            },
                            "transitTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 0,
                                "maxValue": 0,
                                "unitCode": "h",
                            },
                        },
                    },
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": data["rate"],
                    "bestRating": data["best_rate"],
                    "worstRating": data["worst_rate"],
                    "ratingCount": data["rate_count"],
                },
            }
        elif type == "Video":
            res = {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": self.title,
                "description": self.desc,
                "thumbnailUrl": self.img_url if self.img_url else "",
                "uploadDate": (
                    self.datetime.strftime("%Y-%m-%d") if self.datetime else ""
                ),
                "duration": f"PT{data['min']}M{data['sec']}S",
                "contentUrl": self.url,
            }
        elif type == "Site":
            res = {
                "@context": "https://schema.org/",
                "@type": "WebSite",
                "name": site,
                "url": self.url,
            }
        else:
            res = {}

        return json.dumps(res, ensure_ascii=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.generate_meta()
        context["meta"] = self.meta_data
        context["meta"]["schemas"] = [self.get_schema(**self.schema_kwargs)]

        return context


class ArticleView(MetaView, DetailView):

    def get_context_data(self, **kwargs):
        self.title = self.object.title
        self.desc = self.object.desc
        self.keyw = self.object.label
        self.img_url = f"https://{DOMAIN}/media/{self.object.image}"
        img_size = Image.open(self.object.image).size
        self.img_size = f"{img_size[0]}*{img_size[1]}"
        self.datetime = self.object.update
        self.publish_datetime = self.object.create
        self.have_video = False
        self.have_picture = True
        self.follow = True
        self.page_type = "Article"
        self.schema_kwargs = {
            "type": "Article",
            "site": SITE,
            "site_logo": f"https://{DOMAIN}/{LOGO_PATH}",
            "art_type": "BlogPosting",
            "author_type": "Organization",
            "author": SITE,
        }
        return super().get_context_data(**kwargs)


class PageView(MetaView, DetailView):

    def get_context_data(self, **kwargs):
        self.title = self.object.title
        self.desc = self.object.desc
        self.keyw = self.object.label
        self.img_url = f"https://{DOMAIN}/media/{self.object.image}"
        img_size = Image.open(self.object.image).size
        self.img_size = f"{img_size[0]}*{img_size[1]}"
        self.datetime = None
        self.have_video = False
        self.have_picture = True
        self.follow = True
        self.page_type = "Website"
        self.schema_kwargs = {
            "type": "Site",
            "site": SITE,
            "site_logo": f"https://{DOMAIN}/{LOGO_PATH}",
        }
        return super().get_context_data(**kwargs)


class ProductView(MetaView, DetailView):

    def get_context_data(self, **kwargs):
        self.title = self.object.title
        self.desc = self.object.desc
        self.keyw = self.object.label
        self.img_url = f"https://{DOMAIN}/{self.object.image}"
        try:
            img_size = Image.open(self.object.image).size
            self.img_size = f"{img_size[0]}*{img_size[1]}"
        except FileNotFoundError:
            pass
        self.have_video = False
        self.have_picture = True
        self.follow = True
        self.datetime = None
        self.publish_datetime = None
        self.page_type = "Product"
        self.schema_kwargs = {
            "type": "Product",
            "site": SITE,
            "site_logo": f"https://{DOMAIN}/{LOGO_PATH}",
            "price": f"{self.object.price * 10}",
            "rate": "4.9",
            "best_rate": "5",
            "worst_rate": "0",
            "rate_count": f"{self.object.records.all().count()}",
        }
        return super().get_context_data(**kwargs)


class ArticleAbstract:
    content: str
    label: list

    @property
    def reading_time(self) -> int:
        WORD_PER_MIN = 200
        soup = BeautifulSoup(self.content, "html.parser")
        text = soup.get_text()

        words = re.findall(r"\b\w+\b", text)
        num_words = len(words)
        reading_time = num_words / WORD_PER_MIN

        return round(reading_time)

    @property
    def clean_content(self):
        soup = BeautifulSoup(self.content, "html.parser")

        # Delete (style, width, height, class, id) attribute from any tag
        for tag in soup.find_all(True):
            for attr in ["style", "width", "height", "class", "id"]:
                if attr in tag.attrs:
                    del tag.attrs[attr]

        # p
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if "\xa0" == text or text == "":
                p.decompose()
            else:
                p["class"] = p.get("class", []) + "text-justify".split(" ")

        # a
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href", "")

            # Replace Aparat
            if href.startswith("https://www.aparat.com/embed"):
                a_title = a_tag.string
                a_tag.string = ""

                div_tag = soup.new_tag("div")
                aparat_id = href[
                    href.index("[rnddiv]") + 9 : href.index("&data[responsive]")
                ]
                div_tag["id"] = aparat_id
                script_tag = soup.new_tag("script", type="text/JavaScript", src=href)
                div_tag.append(script_tag)

                div_wrapper = soup.new_tag(
                    "div", **{"class": "aparat w-100 cen-col my-5"}
                )
                div_wrapper.append(div_tag)

                video_title = soup.new_tag(
                    "p", **{"class": "text-center mt-3 text-secondary"}
                )
                video_title.string = a_title
                div_wrapper.append(video_title)

                a_tag.replace_with(div_wrapper)
            # Blank
            else:
                a_tag["target"] = "_blank"

        # figure
        for figure in soup.find_all("figure"):
            figure["class"] = "w-100 cen-col my-5 overflow-auto".split(" ")

            img_tag = figure.find("img")
            if img_tag:
                img_src = img_tag["src"]

                img = Image.open(img_src[1:])  # 1: "/media/" to "media/"
                width, height = img.size

                # Small images
                if width < 400:
                    previous_element = figure.find_previous_sibling()
                    if previous_element and not previous_element.name.startswith("h"):
                        div = soup.new_tag("div")
                        div["class"] = "cen-row w-100".split(" ")
                        figure["class"] = "cen-col col-12 col-md-6 col-lg-4".split(" ")
                        previous_element["class"] = "col-12 col-md-6 col-lg-8".split(
                            " "
                        )
                        previous_element_previous = previous_element.find_previous()
                        div.append(previous_element)
                        div.append(figure)
                        previous_element_previous.insert_after(div)

        # Table
        for table in soup.find_all("table"):
            table["class"] = table.get("class", []) + "table table-bordered minw".split(
                " "
            )

        # Delete all &nbsp; character and convert to empty
        for element in soup.find_all(string=True):
            updated_text = element.replace("\xa0", " ").replace("ي", "ی")
            element.replace_with(updated_text)

        # Look for heading tags (h2, h3, h4), add an id, create ArticleTree
        toc = []
        for heading in soup.find_all(["h2", "h3", "h4"]):
            heading_text = heading.get_text(strip=True)
            heading_id = heading_text.replace(" ", "-").upper()
            heading["id"] = heading_id

            if heading.name == "h2":
                toc.append(
                    {"level": 2, "text": heading_text, "id": heading_id, "sub": []}
                )
            elif heading.name == "h3" and toc:
                toc[-1].setdefault("sub", []).append(
                    {"level": 3, "text": heading_text, "id": heading_id, "sub": []}
                )
            elif heading.name == "h4" and toc and "sub" in toc[-1] and toc[-1]["sub"]:
                toc[-1]["sub"][-1].setdefault("sub", []).append(
                    {"level": 4, "text": heading_text, "id": heading_id}
                )

        # Create the nested TOC as <nav>
        nav = soup.new_tag("nav")
        nav["class"] = "article-menu bg-fl-main col-12 col-md-6 col-lg-4".split(" ")

        def build_toc(toc_list):
            ul = soup.new_tag("ul")
            for item in toc_list:
                li = soup.new_tag("li")
                a = soup.new_tag(
                    "a", href=f"#{item['id']}", role="button", title=item["text"]
                )
                a.string = item["text"]
                li.append(a)
                if "sub" in item:
                    li.append(build_toc(item["sub"]))
                ul.append(li)
            return ul

        p = soup.new_tag("p")
        p.string = "آنچه در این مقاله میخوانید:"
        nav.append(p)

        nav.append(build_toc(toc))
        soup.insert(0, nav)
        return str(soup)

    @property
    def dashed_label(self):
        new = []
        for label in self.label:
            new.append(label.replace(" ", "_"))

        return new
