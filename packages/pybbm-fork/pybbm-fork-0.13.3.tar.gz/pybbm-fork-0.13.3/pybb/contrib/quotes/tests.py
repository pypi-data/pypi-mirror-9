from django.core.urlresolvers import reverse

from django.utils.html import strip_spaces_between_tags as minify_html

from pybb.tests.base import TestCase

from .models import Quote
from .processors import QuoteProcessor
from . import settings as quotes_settings

from pybb.models import Post


class QuotesTest(TestCase):
    def test_simple_quote(self):
        post = Post(user=self.staff, body='[quote="zeus;%d"]Super quote[/quote]' % self.post.pk, topic=self.topic)
        post.save()

        self.assertEqual(minify_html(post.body_html), u'<blockquote><div class="quote-author">        Posted by <a class="quote-author-name" href="/users/zeus/">zeus</a><a rel="nofollow" class="quote-message-link" href="/xfoo/1-etopic#post1"></a></div><div class="quote-message">        Super quote    </div></blockquote>')

        self.assertEqual(Quote.objects.filter(from_post=post).count(), 1)

    def test_double_quote(self):
        post = Post(user=self.staff, body='[quote="%s;%d"]%s[/quote]' % (self.post.user.username,
                                                                         self.post.pk,
                                                                         self.post.body),
                    topic=self.topic)
        post.save()

        post = Post(user=self.superuser, body='[quote="%s;%d"]%s[/quote]' % (post.user.username,
                                                                             post.pk,
                                                                             post.body), topic=self.topic)
        post.save()

        self.assertEqual(minify_html(post.body_html), u'<blockquote><div class="quote-author">        Posted by <a class="quote-author-name" href="/users/thoas/">thoas</a><a rel="nofollow" class="quote-message-link" href="/xfoo/1-etopic#post2"></a></div><div class="quote-message"><blockquote><div class="quote-author">        Posted by <a class="quote-author-name" href="/users/zeus/">zeus</a><a rel="nofollow" class="quote-message-link" href="/xfoo/1-etopic#post1"></a></div><div class="quote-message">        bbcode <strong>test</strong></div></blockquote></div></blockquote>')

        self.assertEqual(Quote.objects.filter(from_post=post).count(), 2)

    def test_multiple_quote_add(self):
        self.user
        self.login_as(self.staff)

        self.post

        post = Post(topic=self.topic, user=self.superuser, body='[b]do you want my pere nowel?[/b]')
        post.save()

        response = self.client.post(reverse('quote'), data={
            'topic_id': self.topic.pk,
            'post_id': post.pk
        })

        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('pybb:post_create',
                                           kwargs={'topic_id': self.topic.id}) + '?quote_id=%d' % self.post.id)

        self.assertEqual(response.context['form'].initial['body'], u'[quote="zeus;1"]bbcode [b]test[/b][/quote]\n\n[quote="oleiade;2"][b]do you want my pere nowel?[/b][/quote]\n\n')

        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('quote'), data={
            'topic_id': self.topic.pk,
            'post_id': post.pk
        })

        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('pybb:post_create',
                                           kwargs={'topic_id': self.topic.id}))
        self.assertTrue('body' not in response.context['form'].initial)
        self.assertEqual(response.status_code, 200)

    def test_emmbedded_quotes_preprocessor(self):
        body = 'actual message[quote="zeus;1"]first level[quote="oleiade;2"]second level[quote="zeus;1"]third level[/quote]second level[/quote]first level[/quote]actual message'
        qp = QuoteProcessor(body=body)
        # test all depths
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = 0
        self.assertEqual(qp.render(), u'actual messageactual message')
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = 1
        self.assertEqual(qp.render(), u'actual message[quote="zeus;1"]first levelfirst level[/quote]actual message')
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = 2
        self.assertEqual(qp.render(), u'actual message[quote="zeus;1"]first level[quote="oleiade;2"]second levelsecond level[/quote]first level[/quote]actual message')
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = 3
        self.assertEqual(qp.render(), body)
        # check that deeper depth do not break
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = 4
        self.assertEqual(qp.render(), body)
        # negative depth deactivate the render
        quotes_settings.PYBB_QUOTES_MAX_DEPTH = -1
        self.assertEqual(qp.render(), body)
