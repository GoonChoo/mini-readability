import urllib.request
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup
import textwrap

class Tag:
    _name = None

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self.start() + self.close() + ' ' + self.stop()

    def __repr__(self):
        return self.__str__()

    def start(self):
        return self.open() + self._name

    def stop(self):
        return self.open() + '/' + self._name + self.close()

    @staticmethod
    def close():
        return '>'

    @staticmethod
    def open():
        return '<'

    @staticmethod
    def comment_start():
        return '!'


class MiniHtmlParser:
    __html_raw = ''
    _current_tag = None
    _index = 0

    def __init__(self, html_raw):
        self.__html_raw = html_raw

    def get_next_tag_name(self):
        # find open tag
        start = -1
        while self._index < len(self.__html_raw):
            start = self.__html_raw.find(Tag.open(), self._index)
            if start == -1:
                return None

            # skip '</' close tag start or '!'
            if self.__html_raw[start+1] == '/' or self.__html_raw[start+1] == '!':
                stop = self.__html_raw.find(Tag.close(), start)
                if stop == -1:
                    return None
                self._index = stop
            else:
                self._index = start
                break

        if start == -1:
            return None
        stop = self.__html_raw.find('>', start)
        if stop == -1:
            return None
        tag_name = self.__html_raw[start+1:stop]

        name_space_index = tag_name.find(' ')
        if name_space_index != -1:
            tag_name = tag_name[:name_space_index]
        if len(tag_name) > 0:
            self._index = stop + 1
            self._current_tag = Tag(tag_name)
            return tag_name
        return None

    def get_data_current_tag(self):
        index_stop = self.__html_raw.find(self._current_tag.stop(), self._index)
        s = self.__html_raw[self._index:index_stop]
        self._index = index_stop
        return s


class MiniReadability:
    def __init__(self, url):
        self._url = url

    @property
    def get_article(self):
        article_text = ''
        tags_with_text = self.get_default_meta_tags()
        # print(tags_with_text)
        with urllib.request.urlopen(self._url) as f:
            html_raw = f.read().decode('utf-8')
            # print(html_raw)
            # strings = self.get_article(html_raw, tags_with_text)

            # шаблон для мета тегов разметки, внутри которых может быть текст
            meta_tags = ['div']
            # шаблон для тегов в которых есть текст
            text_tags = ['p', 'h1']
            # поиск всех мета тэгов, в которых есть тэги с текстом
            # получаем словарь {node: text_len}
            nodes_with_text_tags = self._get_nodes_with_text(html_raw, meta_tags, text_tags)
            for key, value in nodes_with_text_tags.items():
                print('node %s : %s text tags number = %d' % (key.tag, key.attrib, value))

            # находим среди всех мета тэгов, тэг с наибольшим количеством текста
            max_text_len = max(nodes_with_text_tags.values())
            print('max text tags number in node = %d' % max_text_len)
            fattest_nodes = [key for key, value in nodes_with_text_tags.items() if value == max_text_len]
            print('fattest nodes:')
            for node in fattest_nodes:
                print('node %s : %s' % (node.tag, node.attrib))
            # если
            # TODO: remove magic number
            if len(fattest_nodes) > 1:
                # TODO: добавить фильтр на длину реального текста, а не количества тэгов с текстом
                pass

            # поднимаемся на к родителю выбранного нода,
            # чтобы найти возможный заголовок и остальные абзацы
            if len(fattest_nodes) > 0:
                big_fat_node = fattest_nodes[0]
            else:
                return ''

            root_node = big_fat_node.getparent()
            if root_node is None:
                root_node = big_fat_node
            print('root node %s : %s' % (root_node.tag, root_node.attrib))

            article_text = self._get_text_nodes_from_parent(root_node, text_tags)

        return article_text

    @property
    def get_article_bs(self)-> str:
        article_text = ''
        meta_tags = self.get_default_meta_tags()
        text_tags = self.get_default_text_tags()
        delete_tags = self.get_default_deleted_tags()
        with urllib.request.urlopen(self._url) as f:
            #TODO: добавить поиск шаблонов по имени сайта
            html_raw = f.read().decode('utf-8')
            root_bs = BeautifulSoup(html_raw, "html.parser")
            text_nodes = self._get_nodes_with_text_bs(root_bs, meta_tags, text_tags, delete_tags)
            # for node in text_nodes:
            #     print(node)
            if len(meta_tags) == 0:
                # сайт был без шаблона, надо найти <div> с самым длинным текстом
                fat_text_node = self.get_parent_node_with_longest_text(text_nodes)
                text_nodes = self._get_text_nodes_from_parent(fat_text_node, text_tags)
            article_text = self._get_text_from_nodes(text_nodes, [])
        return article_text

    @staticmethod
    def get_default_meta_tags():
        return []

    @staticmethod
    def get_default_text_tags():
        return ['p']

    @staticmethod
    def get_default_deleted_tags():
        return ['footer']

    def _get_nodes_with_text_bs(self, root_bs, meta_tags, text_tags, delete_tags)-> list:
        delete_nodes = root_bs.find_all(delete_tags)
        for delete in delete_nodes:
            delete.extract()

        nodes_with_text_tags = []
        if len(meta_tags) > 0:
            # TODO: add find all meta nodes
            pass
        else:
            nodes_with_text_tags.append(root_bs)

        node_text = root_bs.find_all(text_tags)
        return node_text

    @staticmethod
    def get_parent_node_with_longest_text(text_nodes):
        parents = {}
        for node in text_nodes:
            parent = node.parent
            if parent in parents.keys():
                parents[parent] += len(node.text)
            else:
                parents.update({parent: len(node.text)})
        # for key, value in parents.items():
        #     print(key.name + ' : ', end='')
        #     print(key.attrs)
        #     print(value)
        #     print()
        max_len = max(parents.values())
        max_node = [key for key, value in parents.items() if value == max_len]
        return max_node[0]

    @staticmethod
    def _get_text_nodes_from_parent(node, text_tags) ->str:
        return node.find_all(text_tags)

    @staticmethod
    def _get_text_from_nodes(text_nodes, tags_replace_template)-> str:
        text = ''
        for node in text_nodes:
            refs = node.find_all('a')
            for ref in refs:
                ref_str = ref.text + ' [' + ref.get('href') + ']'
                ref.replaceWith(ref_str)
            text += '\n'.join(textwrap.wrap(node.text)) + '\n\n'
        return text

    # def _get_children_max_depth(self, node, tag_name) ->int:
    #     children = node.xpath('./' + tag_name)
    #     if len(children) == 0:
    #         return 0
    #     children_depths = []
    #     for child in children:
    #         children_depths.append(self._get_children_max_depth(child, tag_name))
    #     return 1 + max(children_depths)

    def _get_nodes_with_text(self, html_raw, meta_tags, text_tags) ->dict:
        nodes_with_text = {}
        tree = html.fromstring(html_raw)
        div_nodes = tree.xpath('//div')

        for node in div_nodes:
            text_tags_count = 0
            for text_t in text_tags:
                text_children = node.xpath('./' + text_t)
                text_tags_count += len(text_children)
            # print(node.attrib)
            # print('children tags with text for node = %d' % text_tags_count)
            # print()
            if text_tags_count > 0:
                nodes_with_text.update({node: text_tags_count})
        return nodes_with_text
