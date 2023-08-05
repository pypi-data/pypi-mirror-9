# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models import Min
from django.test import TestCase
from django.utils import timezone
from facebook_applications.models import Application
from facebook_comments.factories import CommentFactory
from facebook_pages.factories import PageFactory
from facebook_users.models import User
from .factories import PostFactory
from .models import Post, PostOwner, Comment, Page

PAGE_ID = '19292868552'
POST1_ID = '19292868552_10150189643478553'
POST2_ID = '100001341687090_632170373504346'
COMMENT1_ID = '19292868552_10150475844632302_20258978'

PAGE1_ID = '1411299469098495'
GROUP_CLOSED_ID = '167276666692692'

POST_WITH_MANY_LIKES_ID = '19292868552_10151516882688553'
POST_WITH_MANY_COMMENTS_ID = '19292868552_10150475844632302'


class FacebookPostsTest(TestCase):
    def test_fetch_post(self):
        self.assertEqual(Post.objects.count(), 0)
        Post.remote.fetch(POST1_ID)
        Post.remote.fetch(POST1_ID)
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.all()[0]

        self.assertEqual(post.graph_id, POST1_ID)
        self.assertEqual(post.link, u'http://developers.facebook.com/blog/post/497')
        self.assertEqual(post.name, u'Developer Roadmap Update: Moving to OAuth 2.0 + HTTPS')
        self.assertEqual(post.type, 'link')
        self.assertEqual(post.status_type, 'published_story')
        self.assertIsInstance(post.created_time, datetime)
        self.assertTrue('We continue to make Platform more secure for users' in post.description)
        self.assertGreater(len(post.icon), 0)
        self.assertGreater(len(post.picture), 20)

    def test_post_fetch_application(self):
        Post.remote.fetch(POST1_ID)
        post = Post.objects.all()[0]
        application = Application.objects.all()[0]

        application_json = {
            "name": "NetworkedBlogs",
            "namespace": "blognetworks",
            "id": "9953271133"
        }
        self.assertEqual(post.application, application)
        self.assertEqual(post.application.graph_id, application_json['id'])
        self.assertEqual(post.application.name, application_json['name'])
        self.assertEqual(post.application.namespace, application_json['namespace'])

    def test_post_fetch_authors_owners(self):
        # post on the page by page
        author = {
            "name": "Facebook Developers",
            "category": "Product/service",
            "id": "19292868552"
        }
        Post.remote.fetch(POST1_ID)
        post = Post.objects.get(graph_id=POST1_ID)
        page = Page.objects.get(graph_id=author['id'])

        self.assertEqual(page.graph_id, author['id'])
        self.assertEqual(page.name, author['name'])
        self.assertEqual(page.category, author['category'])

        self.assertEqual(post.author_json, author)
        self.assertEqual(post.author, page)

        # post on the page by user
        author = {
            "id": "100000550622902",
            "name": "Danny Reitzloff"
        }
        owners = [{
                      "id": "100001341687090",
                      "name": "Rainbow Gathering"
                  }]

        Post.remote.fetch(POST2_ID)
        post = Post.objects.get(graph_id=POST2_ID)
        user = User.objects.get(graph_id=author['id'])
        postowner = PostOwner.objects.all()[0]

        self.assertEqual(post.author, user)
        self.assertEqual(post.owners.all()[0], postowner)
        # self.assertEqual(post.owners_json, owners) # TODO: fix saving json as string
        self.assertDictEqual(post.author_json, author)

        self.assertEqual(user.graph_id, author['id'])
        self.assertEqual(user.name, author['name'])

        self.assertEqual(postowner.owner.name, owners[0]['name'])
        self.assertEqual(postowner.owner.graph_id, owners[0]['id'])

    def test_post_fetch_comments(self):
        post = PostFactory(graph_id=POST_WITH_MANY_COMMENTS_ID)

        self.assertEqual(Comment.objects.count(), 0)

        comments = post.fetch_comments(limit=100)
        self.assertEqual(comments.count(), 100)
        self.assertEqual(comments.count(), Comment.objects.count())
        self.assertEqual(comments.count(), post.comments.count())

        comments = post.fetch_comments(all=True)
        self.assertGreater(post.comments_count, 1000)
        self.assertEqual(post.comments_count, Comment.objects.count())
        self.assertEqual(post.comments_count, comments.count())
        self.assertEqual(post.comments_count, post.comments.count())

        comment = comments.get(graph_id=COMMENT1_ID)
        user = User.objects.get(graph_id='100000422272038')

        self.assertEqual(user.name, 'Jordan Alvarez')

        self.assertEqual(comment.owner, post)
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.message, 'PLAYDOM? bahhhhhhhhh ZYNGA RULES!')
        self.assertEqual(comment.can_remove, False)
        self.assertEqual(comment.user_likes, False)
        self.assertIsInstance(comment.created_time, datetime)
        self.assertGreater(comment.likes_count, 5)

    def test_post_fetch_likes(self):
        post = PostFactory(graph_id=POST_WITH_MANY_LIKES_ID)

        self.assertEqual(post.likes_users.count(), 0)
        self.assertEqual(User.objects.count(), 1)

        users = post.fetch_likes(all=True)
        self.assertGreater(users.count(), 1000)
        self.assertEqual(post.likes_count, users.count())
        self.assertEqual(post.likes_count, User.objects.count() - 1)
        self.assertEqual(post.likes_count, post.likes_users.count())

    def test_comment_fetch_likes(self):
        post = PostFactory(graph_id=POST1_ID)
        comment = CommentFactory(graph_id=COMMENT1_ID, owner=post)

        self.assertEqual(comment.likes_users.count(), 0)
        self.assertEqual(User.objects.count(), 2)

        users = comment.fetch_likes(all=True)
        self.assertGreater(users.count(), 7)
        self.assertEqual(comment.likes_count, users.count())
        self.assertEqual(comment.likes_count, User.objects.count() - 2)
        self.assertEqual(comment.likes_count, comment.likes_users.count())

    def test_post_fetch_shares(self):
        post = PostFactory(graph_id=POST_WITH_MANY_LIKES_ID)

        self.assertEqual(post.shares_users.count(), 0)
        self.assertEqual(User.objects.count(), 1)

        users = post.fetch_shares(all=True)
        self.assertGreaterEqual(users.count(), 40)
        self.assertEqual(post.shares_count, users.count())
        self.assertEqual(post.shares_count, User.objects.count() - 1)
        self.assertEqual(post.shares_count, post.shares_users.count())

        post = PostFactory(graph_id='1411299469098495_1534163126812128')
        users = post.fetch_shares(all=True)
        self.assertGreaterEqual(users.count(), 7)

        count = users.count()

        users = post.fetch_shares(all=True)
        self.assertEqual(users.count(), count)

    # def test_page_fetch_posts_with_strange_object_id(self):
    #     instance = PageFactory(graph_id=252974534827155)
    #     posts = instance.fetch_posts(all=True, since=datetime(2014, 9, 1).replace(tzinfo=timezone.utc))
    #
    #     self.assertEqual(posts.filter(graph_id='252974534827155_323648421093099')[0].object_id, None)

    def test_page_fetch_posts(self):
        page = PageFactory(graph_id=PAGE_ID)

        self.assertEqual(Post.objects.count(), 0)

        posts = page.fetch_posts()

        self.assertEqual(posts.count(), 25)
        self.assertEqual(posts.count(), Post.objects.count())

        earliest = posts.aggregate(Min('created_time'))['created_time__min'] - timedelta(30)
        posts = page.fetch_posts(all=True, since=earliest)

        self.assertGreater(posts.count(), 25)
        self.assertEqual(posts.count(), Post.objects.count())

        earliest1 = posts.aggregate(Min('created_time'))['created_time__min']
        self.assertTrue(earliest <= earliest1)

        # posts = page.fetch_posts(all=True, limit=95)
        # posts_count = Post.objects.count()
        #
        # self.assertGreaterEqual(posts.count(), 95)
        # self.assertEqual(posts.count(), posts_count)

        Post.objects.all().delete()
        posts = page.fetch_posts(all=True, since=timezone.now() - timedelta(10))

        self.assertEqual(posts.count(), Post.objects.count())
        self.assertLess(posts.count(), 25)

        # def test_group_closed_fetch_posts(self):
        # page = PageFactory(graph_id=GROUP_CLOSED_ID)
        #
        #     self.assertEqual(Post.objects.count(), 0)
        #
        #             posts = page.fetch_posts(all=True)
        #
        #     self.assertTrue(len(posts) > 0) # ensure user has access to closed group

    def test_page_fetch_many_posts(self):
        page = PageFactory(graph_id=PAGE1_ID)

        self.assertEqual(Post.objects.count(), 0)

        posts = page.fetch_posts(all=True, since=datetime(2014, 1, 1).replace(tzinfo=timezone.utc))

        self.assertGreater(posts.count(), 250)
        self.assertEqual(posts.count(), Post.objects.count())
        self.assertTrue(posts.filter(created_time__lte=datetime(2014, 1, 7).replace(tzinfo=timezone.utc)).count(), 1)
