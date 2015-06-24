/* Javascript for cs101XBlock. */
function ImageCodingXBlockInitView(runtime, element) {
    var handlerUrl = runtime.handlerUrl(element, 'student_submit');
    var hintUrl = runtime.handlerUrl(element, 'get_hint');
	var publishUrl = runtime.handlerUrl(element, 'publish_event');

	var $element = $(element);
	
    var submit_button = $element.find('.submit_button');
    var hint_button = $element.find('hint_button');
    var reset_button = $element.find('.reset_button');

    var unanswered = $element.find('.unanswered');
    var correct = $element.find('.correct');
    var incorrect = $element.find('.incorrect');

    var correct_feedback = $element.find('.correct_feedback');

    var hint_div = $element.find('.hint');

	var hint_counter = 0;
    var student_code = "";
    
	//var ta = document.getElementById('jsinputid');
	//var initial_code = ta.value;

    var hint;
    var hints;
    var hint_counter = 0;
	
    //$.ajax({
    //    type: 'POST',
    //    url: hintUrl,
    //    data: JSON.stringify({requested: true}),
    //    success: set_hints
    //});

    function publish_event(data) {
      $.ajax({
          type: "POST",
          url: publishUrl,
          data: JSON.stringify(data)
      });
    }

	function post_submit(result) {
	}
	
	function set_hint(result) {
	    console.log('set_hint:' + result);
	    //hint_button.css('display','inline');
		//hint_button_holder.css('display','inline');
		hint_div.css('display','inline');
		hint_div.html(result.hint);
		hint_div.attr('hint_index', result.hint_index);
	}

	function show_unanswered() {
		console.log('show_unanswered');
		unanswered.css('display','block');
		correct.css('display','none');
		incorrect.css('display','none');
		correct_feedback.css('display','none');
	}

	function show_correct() {
		console.log('show_correct');
		unanswered.css('display','none');
		correct.css('display','block');
		incorrect.css('display','none');
		correct_feedback.css('display','block');
	}

	function show_incorrect() {
		console.log('show_incorrect');
		unanswered.css('display','none');
		correct.css('display','none');
		incorrect.css('display','block');
		correct_feedback.css('display','none');
	}

    function reset_answer() {
		hint_div.css('display','none');
		show_unanswered();
		try {
			clearOutput();
		}
		catch (e) {
		}
		var ta = document.getElementById('jsinputid');
		ta.value = initial_code;
    }

    function reset_hint() {
        return;
    	hint_counter = 0;
    	hint_div.css('display','none');
    }

    function show_hint() {
        return;
    	hint = hints[hint_counter];
		hint_div.html(hint);
		hint_div.css('display','block');
		publish_event({
			event_type:'hint_button',
			next_hint_index: hint_counter,
		});
		if (hint_counter == (hints.length - 1)) {
			hint_counter = 0;
		} else {
			hint_counter++;
		}
    }

    $('.submit_button', element).click(function(eventObject) {
        var correct = false;
  		try {
  		    //debugger
  		    // TODO: seems like it should be possible to store the id in the this rather than the following
  		    var id = $(this).parent().parent().parent().find('.student_code')[0].id;
  			correct = evaluateGrade(id);
  		}
  		catch (e) {
  		    console.log('ERROR is submit grading:' + e);
  		}
  		console.log('correctness in submit:' + correct);
  		
  		
  		correct_bool = (correct && correct != 'notready');  // can be "notready"
  		
        // We AJAX save both their data and the correctness
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify({'student_code': $('.student_code',element).val(), 'correct': correct_bool }),
            success: post_submit
        });
        
        if (correct == 'notready') {
            alert('Please Run first to produce output, then try Submit');
        }

  		// Now update the UI .. this should always be in sync with what we stored
  		// TODO: could store persistently the correctness, so it looks right when they come back .. probably what
        if (correct_bool) {
        	show_correct();
        } else {
        	show_incorrect();
        }
	});
	

    $('.run_button', element).click(function(eventObject) {
        // "this" is the input element, so we jquery from there to find the correct textarea
        var id = $(this).parent().parent().find('.student_code')[0].id;
  		evaluateClear(id);
  		
  		// TODO: not set up to do this on the main thread
  		// solution: provide fn pointer to evaluate clear, it calls that
  		/*
		var ta = document.getElementById(id);
		var text = ta.value;
  		var grade = evaluateGrade(id);
  		console.log('grade in run:' + grade);
  		*/

// 		publish_event({
// 			event_type:'run_button',
// 			student_code: text,
// 		});
	});

    $('.hint_button', element).click(function(eventObject) {
        var next_index, hint_index = hint_div.attr('hint_index');
        if (hint_index == undefined) {
            next_index = 0;
        }
        else {
            next_index = parseInt(hint_index) + 1;
        }
        $.ajax({
        type: 'POST',
        url: hintUrl,
        data: JSON.stringify({'hint_index': next_index}),
        success: set_hint
        });
	});

//         $.ajax({
//             type: 'POST',
//             url: handlerUrl,
//             data: JSON.stringify({'student_code': $('.student_code',element).val(), 'correct': correct_bool }),
//             success: post_submit
//         });
//         data: JSON.stringify({requested: true}),

    //$('.reset_button', element).click(function(eventObject) {
    //    reset_answer();
	//});
	
 
}


