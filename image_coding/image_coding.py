""" Image Coding main Python class """

"""
Things TBD
-log syntax errors on Run button
-Think about how we prompt students who click Submit but not Run
-Think about showing the green/red correctly when they reload/revisit a prob
-When they click Run again .. maybe blank out the red/green marking?
-Maybe fiddle with font/layout, use monospace
 -The text area should definitely be resizeable

Maybe:
-Rename to be more generic
-Could permit the .js includes to be static resources vs. putting them in here: easier rev
 -e.g. that's how course triple should work
"""


import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, String, List, Float, Boolean
from xblock.fragment import Fragment

# from lxml import etree
# from xml.etree import ElementTree as ET
# 
# from StringIO import StringIO
# 
# import textwrap

class ImageCodingXBlock(XBlock):
    icon_class = 'other'  # vs. video etc.

    display_name = String(display_name='Display Name',
        default='Image Coding',
        scope=Scope.settings,
        help='This name appears in the horizontal navigation at the top of the page.')

    # TODO Scope.settings vs. Scope.content
    body = String(
        default='<p>Body goes here</p>', 
        scope=Scope.settings,
        help='Body html',
    )

    solution_code = String(
        default='Solution code goes here', 
        scope=Scope.settings,
        help='Solution code',
    )

    starter_code = String(
        default='Starter code goes here', 
        scope=Scope.settings,
        help='Starter code',
    )

    student_code = String(
        default='', 
        scope=Scope.user_state,
        help='The student authored code',
    )

    stored_success = Boolean(
        default=False, 
        scope=Scope.user_state,
        help='Cache question success state, so UI looks right'
    )

    tolerance = String(
        default='', 
        scope=Scope.settings,
        help='Tolerance number for image grading',
    )

    regex = String(
        default='', 
        scope=Scope.settings,
        help='Regular expression for grading text output',
    )

    hints = String(
        default='',
        scope=Scope.settings,
        help='Hints for the question, one per line',
    )

    # These are needed to have scoring
    weight = Float(
        display_name="Weight",
        help="This is the maximum score that the user receives when he/she successfully completes the problem",
        scope=Scope.settings,
        default=1
    )
    has_score = True


    def student_view(self, context=None):
        """Student view of the problem, complete with Run button and grading"""
        ##import pdb
        ##pdb.set_trace()
        
        correct_icon_url = self.runtime.local_resource_url(self, 'public/images/correct-icon.png')
        incorrect_icon_url = self.runtime.local_resource_url(self, 'public/images/incorrect-icon.png')
        unanswered_icon_url = self.runtime.local_resource_url(self, 'public/images/unanswered-icon.png')


        # bootstrap logic - trigger on empty student code
        # TODO: could more precisely notice that the student has not written anything
        student_code = self.student_code
        if (student_code.strip() == ''):
            student_code = self.starter_code
        
        html = self.resource_string('static/html/image_coding_view.html')
        #import pdb
        #pdb.set_trace()
        import urllib
        
        hint_button_css = 'display:none'
        if self.hints:
            hint_button_css = 'display:inline'
        frag = Fragment(html.format(self=self,
                                    hint_button_css=hint_button_css,
                                    solution_encoded=urllib.quote(self.solution_code).replace('%', '\\'),
                                    regex_encoded=urllib.quote(self.regex).replace('%', '\\'),
                                    unique_id=self.get_unique_id(),
                                    correct_icon_url=correct_icon_url,
                                    incorrect_icon_url=incorrect_icon_url,
                                    unanswered_icon_url=unanswered_icon_url
                                    ))
        frag.add_css(self.resource_string('static/css/image_coding.css'))
        frag.add_javascript(self.resource_string('static/js/image_coding_view.js'))
        frag.add_javascript(self.resource_string('static/js/image_coding-edx.js'))
        frag.add_javascript(self.resource_string('static/js/image_coding-table-edx.js'))
        frag.initialize_js('ImageCodingXBlockInitView')
        return frag

    @XBlock.json_handler
    def student_submit(self, submissions, suffix=''):
        """Submit/grade from student view.
           -Save the student work student_code
           -Note grading boolean which is included
        """
        #import pdb
        #pdb.set_trace()
        self.student_code = submissions['student_code']
        # the client side javascript creates 'correct'
        is_correct = submissions['correct']  # This is JSONd to a python value
        print 'STORED:', self.stored_success
        if is_correct:
            score = 1
            success = 'success'
            self.stored_success = True
        else:
            score = 0
            success = 'failure'
            self.stored_success = False
        print 'STORED:', self.stored_success
        
        # publish a grading event when student completes this exercise
        # NOTE, we don't support partial credit
        try:
            print 'MEH publish score', score
            self.runtime.publish(self, 'grade', {'value': score, 'max_value': 1})
            print 'MEH done score', score
        except NotImplementedError:
            # TODO: maybe now this is implemented in studio
            pass
            
        # Return our JSON
        msg = '-the message-'
        return {
          'result': success, 'msg': msg
        }


    def studio_view(self, context=None):
        """Studio edit view of the problem, no running or anything, just the data"""
        context = {
            'self': self,
        }
        html = self.render_template('static/html/image_coding_edit.html', context)

        frag = Fragment(html)
        frag.add_javascript(self.load_resource("static/js/image_coding_edit.js"))
        frag.initialize_js('ImageCodingXBlockInitEdit')
        return frag

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        ##import pdb
        ##pdb.set_trace()
        self.display_name = submissions['display_name'].strip()
        self.body = submissions['body']
        self.solution_code = submissions['solution_code']
        self.starter_code = submissions['starter_code']
        self.tolerance = submissions['tolerance'].strip()
        self.regex = submissions['regex'].strip()  # empty turns off the feature, so we're careful here
        self.hints = submissions['hints'].strip().replace('\r', '')

        return {
            'result': 'success',
        }


    @XBlock.json_handler
    def get_hint(self, submissions, suffix=''):
        """Given index, return the hint and its index. Mod around if necessary."""
        import pdb
        #pdb.set_trace()
        hints = self.hints.split('\n')
        hint_index = int(submissions['hint_index'])
        hint_index = hint_index % len(hints)
        hint_text = hints[hint_index]

        # This is basically the code from capa_base to log this case
        event_info = dict()
        event_info['module_id'] = self.location.to_deprecated_string()
        event_info['hint_index'] = hint_index
        event_info['hint_len'] = len(hints)
        event_info['hint_text'] = hint_text
        # TODO: this event name should be something
        self.runtime.track_function('oli.image_coding.demandhint_displayed', event_info)

        return {
            'result': 'success',
            'hint': hint_text,
            'hint_index': hint_index
        }

    '''
    Util functions
    '''
    def get_unique_id(self):
        "Get uniq string to embed in js, stolen from drag-n-drop xblock"
        try:
            unique_id = self.location.name
        except AttributeError:
            # workaround for xblock workbench
            unique_id = self.parent.replace('.', '-')
        return 'nick_' + unique_id

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

#     def _get_body(self, xmlstring):
#         '''
#         Helper method
#         '''
#         tree = etree.parse(StringIO(xmlstring))
#         body = tree.xpath('/image_coding/body')
#         
#         return etree.tostring(body[0], encoding='unicode')

# 
# 		tree = etree.parse(StringIO(self.question_string))
# 		raw_hints = tree.xpath('/image_coding/demandhint/hint')
# 		
# 		decorated_hints = list()
# 		
# 		if len(raw_hints) == 1:
# 			hint = 'Hint: ' + etree.tostring(raw_hints[0], encoding='unicode')
# 			decorated_hints.append(hint)
# 		else:
# 			for i in range(len(raw_hints)):
# 				hint = 'Hint (' + str(i+1) + ' of ' + str(len(raw_hints)) + '): ' + etree.tostring(raw_hints[i], encoding='unicode')
# 				decorated_hints.append(hint)
# 		
# 		hints = decorated_hints	
# 
# 		return {
# 			'result': 'success',
# 			'hints': hints,
# 		}

#     @XBlock.json_handler
#     def publish_event(self, data, suffix=''):
#         try:
#             event_type = data.pop('event_type')
#         except KeyError:
#             return {'result': 'error', 'message': 'Missing event_type in JSON data'}
# 
#         data['user_id'] = self.scope_ids.user_id
#         data['component_id'] = self._get_unique_id()
#         self.runtime.publish(self, event_type, data)
# 
#         return {'result': 'success'}


