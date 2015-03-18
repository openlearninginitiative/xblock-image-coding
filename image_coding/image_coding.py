""" Image Coding main Python class"""

import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, String, List
from xblock.fragment import Fragment

from lxml import etree
from xml.etree import ElementTree as ET

from StringIO import StringIO

import textwrap

class ImageCodingXBlock(XBlock):

    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "other"

    '''
    Fields
    '''
    display_name = String(display_name='Display Name',
        default='Image Coding',
        scope=Scope.settings,
        help='This name appears in the horizontal navigation at the top of the page.')

    student_answer = String(
        default='//Your code here', 
        scope=Scope.user_state,
        help='This is the student\'s answer to the question',
    )
    
    solution = String(
        default='Enter solution here', 
        scope=Scope.content,
        help='This is the solution to the question',
    )
    
    hints = List(
        default=[],
        scope=Scope.content,
        help='Hints for the question',
    )

    question_string =  String(help='Default question content ', 
        scope=Scope.content,
        #default=etree.tostring(question_xml, encoding='unicode', pretty_print=True), 
        default=textwrap.dedent('''
            <image_coding schema_version='1'>
                <body>
                    <p>Add code inside the loop to modify flowers.jpg like this: set each pixel to have green of 0, leaving the red and blue values unchanged. The result should be that the flowers look red, since the yellow was made of red+green light.</p>
                </body>
                <demandhint>
                    <hint>What command sets each pixel to have green of 0?</hint>
                    <hint>To set each pixel to have green of 0, use this command: pixel.setGreen(0);</hint>
                </demandhint>
            </image_coding>
        '''
        ))



    '''
    Main functions
    '''
    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students
        when viewing courses.
        """
 
        prompt = self._get_body(self.question_string)

        correct_icon_url = self.runtime.local_resource_url(self, 'public/images/correct-icon.png')
        incorrect_icon_url = self.runtime.local_resource_url(self, 'public/images/incorrect-icon.png')
        
        attributes = ''
        html = self.resource_string('static/html/image_coding_view.html')
        frag = Fragment(html.format(display_name = self.display_name,
        							prompt = prompt, 
        							solution = self.solution, 
                                    student_answer = self.student_answer, 
                                    unanswered_icon_url = self.runtime.local_resource_url(self, 'public/images/unanswered-icon.png'), 
                                    correct_icon_url = self.runtime.local_resource_url(self, 'public/images/correct-icon.png'), 
                                    incorrect_icon_url = self.runtime.local_resource_url(self, 'public/images/incorrect-icon.png'), 
                                    attributes = attributes
                                    ))
        frag.add_css(self.resource_string('static/css/image_coding.css'))
        frag.add_javascript(self.resource_string('static/js/image_coding_view.js'))
        frag.add_javascript(self.resource_string('static/js/image_coding-edx.js'))
        frag.add_javascript(self.resource_string('static/js/image_coding-table-edx.js'))
        frag.initialize_js('ImageCodingXBlockInitView')
        return frag

    def studio_view(self, context=None):
        '''
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        '''
        context = {
            'display_name': self.display_name,
            'solution': self.solution,
            'xml_data': self.question_string,
        }
        html = self.render_template('static/html/image_coding_edit.html', context)
        
        frag = Fragment(html)
        frag.add_javascript(self.load_resource("static/js/image_coding_edit.js"))
        frag.initialize_js('ImageCodingXBlockInitEdit')
        return frag

    @XBlock.json_handler
    def student_submit(self, submissions, suffix=''):
        '''
        Save student answer
        '''
        self.student_answer = submissions['answer']
        return {'success':True}

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        '''
        Save studio edits
        '''
        self.display_name = submissions['display_name']
        self.solution = submissions['solution']
        xml_content = submissions['data']

        try:
            etree.parse(StringIO(xml_content))
            self.question_string = xml_content
        except etree.XMLSyntaxError as e:
            return {
                'result': 'error',
                'message': e.message
            }

        return {
            'result': 'success',
        }

    @XBlock.json_handler
    def send_hints(self, submissions, suffix=''):
        
		tree = etree.parse(StringIO(self.question_string))
		raw_hints = tree.xpath('/image_coding/demandhint/hint')
		
		decorated_hints = list()
		
		if len(raw_hints) == 1:
			hint = 'Hint: ' + etree.tostring(raw_hints[0], encoding='unicode')
			decorated_hints.append(hint)
		else:
			for i in range(len(raw_hints)):
				hint = 'Hint (' + str(i+1) + ' of ' + str(len(raw_hints)) + '): ' + etree.tostring(raw_hints[i], encoding='unicode')
				decorated_hints.append(hint)
		
		hints = decorated_hints	

		return {
			'result': 'success',
			'hints': hints,
		}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        try:
            event_type = data.pop('event_type')
        except KeyError:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        data['user_id'] = self.scope_ids.user_id
        data['component_id'] = self._get_unique_id()
        self.runtime.publish(self, event_type, data)

        return {'result': 'success'}

    '''
    Util functions
    '''
    def load_resource(self, resource_path):
        '''
        Gets the content of a resource
        '''
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return unicode(resource_content)

    def render_template(self, template_path, context={}):
        '''
        Evaluate a template by resource path, applying the provided context
        '''
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))

    def resource_string(self, path):
        '''Handy helper for getting resources from our kit.'''
        data = pkg_resources.resource_string(__name__, path)
        return data.decode('utf8')

    def _get_body(self, xmlstring):
        '''
        Helper method
        '''
        tree = etree.parse(StringIO(xmlstring))
        body = tree.xpath('/image_coding/body')
        
        return etree.tostring(body[0], encoding='unicode')

    def _get_unique_id(self):
        try:
            unique_id = self.location.name
        except AttributeError:
            # workaround for xblock workbench
            unique_id = 'workbench-workaround-id'
        return unique_id

