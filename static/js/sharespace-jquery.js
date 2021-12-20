$(document).ready(function() {

    ajax_user_query();
    console.log("page ready")



    $("#main_category").change(function(){
		const url = $("#add_item_form").attr("data-sub-cat-url");
		const catID = $(this).val();
        console.log("main cat selected");
		$.ajax({
			url : url,
			data: { 'main_category_id' : catID },
			success : function(data) {
                console.log("ajax request success (cat)");
                console.log(data);
				$("#sec_category").html(data);
			}
		});
	});

    $("#id_user_post_code").keyup(function(){
        let btn = $('#complete-profile-btn').attr('disabled', true);
        let post_code = $('#id_user_post_code').val();
        console.log(post_code);
        const api_url = "https://api.postcodes.io/postcodes/";
        let full_url = api_url + post_code + "/validate";
        console.log(full_url);
        if (post_code.length >= 6){
            let request = new XMLHttpRequest();
            request.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200) {
                    let myData = JSON.parse(this.responseText);
                    console.log(myData);
                    if (myData['status']=== 200 && ! myData['result']){
                        alert("Please enter a valid postcode to continue");
                    }
                    else if (myData['status']=== 200 && myData['result']){
                        btn.removeAttr('disabled');
                    }
                } else {
                    console.log("error at request point" + request.status);
                }
            }
            request.open("GET", full_url);
            request.send();
        }

    });

    $("#id_proposal_cat").change(function (){
        const url = $("#purchase_proposal_form").attr("data-sub-cat-url");
        const catID = $(this).val();
        console.log("cat element selected")

        $.ajax({
            url : url,
            data: {'main_category_id' : catID},
            success : function(data){
                console.log("ajax request success (cat)")
                console.log(data)
                $('#id_proposal_sub_cat').html(data)
            }

        });

    });

    $('#submit-loan-btn').click(function (){
        console.log("button to submit loan clicked")
        const url = $('#borrow-item-form').attr('data-req-url');
        const dateOut = $('#date-borrow-from').val();
        const dateIn = $('#date-borrow-until').val();
        const itemSlug = $('#item-to-borrow').attr('data-item');
        const csrftoken = getCookie('csrftoken')

        console.log("formulating request to server");
        console.log(url);
        console.log(dateIn);
        console.log(dateOut);
        console.log(itemSlug);

        $.ajax({
            url : url,
            type : 'POST',
            headers : {'X-CSRFToken' : csrftoken},
            data : {
                'date_in': dateIn,
                'date_out': dateOut,
                'item_slug': itemSlug
            },
            success : function (data){
                console.log("ajax request done");
                console.log("printing data received (if any)");
                console.log(data);
                $('#msg-p').html(data);
                let msg_section = $('#error-msg-div');
                msg_section.removeAttr('hidden');
                if (data==="loan created"){
                    msg_section.css('background-color', "green");
                    $('#borrow-item-form').toggle();
                }

            }


        });


    });

	$('#returned-item-btn').click(function(){
	    console.log("button in loan page clicked")
	    var loanSlugVar;
	    loanSlugVar = $(this).attr('data-loanslug');
        console.log("loan slug")
        console.log(loanSlugVar)
	    $.get('/sharespace/loan/return/',
	        {'loan_slug': loanSlugVar },
	        function(data){
	            $('#display-result').html("loan completed");
	            $('#returned-item-btn').hide();
	            console.log("ajax request done");
	        }
	    );

	});

    $('.owner-selector').click(function (){
        console.log("other owners selected");
        if ($(this).is(':checked')){
            $('.guardian-selector').prop("disabled", false)
        }else {
            $('.guardian-selector').prop("disabled", true)
            $("input:radio[name=guardian-selector-name]:checked")[0].checked = false
        }


    });

     $('p').hover(
        function() {
            $(this).css('color', 'blue');
        },
        function() {
            $(this).css('color', 'black');
        }
    );
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function ajax_user_query(){
    console.log("profile pic func");
    let link = $('#profile-link');
    let url = link.attr('url-data');
    let username = link.attr('username-data');
    console.log(link)
    console.log(url)
    console.log(username)

        $.ajax({
            url : url,
            data : {'username': username},
            success : function(data){
                console.log(data);
                set_elements(data);
            }
        });
}

function set_elements(data) {
    console.log("set element function");
    if (isEmpty(data)){
        console.log("anonymous user?");
    }

    else{

            console.log(data);
            console.log("in here");
            console.log(typeof data);
            console.log(data.img_path);
            console.log(data.user_url);

            const img_path = data.img_path;


            console.log(img_path);

            var profile_icon = document.getElementById("profile-icon");
            console.log(profile_icon)
            profile_icon.setAttribute("src", img_path);


    }
}


function lookup_func() {
			console.log("post code function exec");
			var url = "https://api.getAddress.io/find/";
			var api_key = "IdUvLkdSBki8uOcIoH01EQ33123";
			var post_code = document.getElementById("add_item_postcode").value;
			var f_post_code = post_code.toLowerCase().replace(' ', '');
			console.log(f_post_code);
			var full_url = url + f_post_code + "?api-key=" + api_key;
			console.log("full url " + full_url)
			var request = new XMLHttpRequest();
			request.onreadystatechange = function(){
			    if(this.readyState === 4 && this.status === 200){
				    var myData = JSON.parse(this.responseText);
				    console.log("here is the data retrieved");
				    console.log(myData);
				    populate_list(myData);
			    }
			    else { console.log("error at request point" + request.status);
                    if (this.readyState ===4 && request.status === 400){
                        const new_elem = document.createElement("p");
                        const text = document.createTextNode("No address was found, please enter address manually");
                        new_elem.append(text);
                        var elem = document.getElementById("address_list");
                        elem.after(new_elem);
                    }

			    }
			};
			request.open("GET", full_url);
			request.send();

}

function populate_list(data) {
    const address_list = data['addresses'];
    var selection = document.getElementById("address_list");
    for (let i = 0; i < address_list.length; i++) {
        var option = document.createElement("option");
        option.text = address_list[i];
        selection.add(option);
    }

}
function populate_address(){
    const sel_adr = document.getElementById("address_list");
    console.log(sel_adr.selectedIndex)
    var str_address = sel_adr.options[sel_adr.selectedIndex].text
    console.log(str_address)
    tokens = str_address.split(',')
    console.log(tokens.length);
    document.getElementById("id_adr_line_1").value = tokens[0];
    document.getElementById("id_adr_line_2").value = tokens[1];
    document.getElementById("id_adr_line_3").value = tokens[2];
    document.getElementById("id_adr_line_4").value = tokens[3];
    document.getElementById("id_locality").value = tokens[4];
    document.getElementById("id_city").value = tokens[5];
    document.getElementById("id_county").value = tokens[6];

}
function load_calendar() {
    console.log("load cal called")
    $(document).ready(function (){
        const elem = $("#availability-calendar");
        const url = elem.attr("data-ajax-url");
        const item_slug = elem.attr("data-item-slug");
        console.log(url)
        $.ajax({
            url : url,
            data : {'item_slug' : item_slug},
            success: function (){

            }

        });

    });

}
function cancel_booking(){
        console.log("button to cancel booking clicked");
        let loanSlugVar;
        let btn = $('#cancel-booking-btn')
        loanSlugVar = btn.attr('data-loanslug');
        let req_url = btn.attr('data-ajax-url');
        console.log("request slug")
        console.log(req_url)
        console.log("loan slug")
        console.log(loanSlugVar)
        const csrftoken = getCookie('csrftoken');

	    $.ajax({
            url : req_url,
            type : 'POST',
            headers : {'X-CSRFToken' : csrftoken},
            data : {'loan_slug' : loanSlugVar},
            success: function (data){

                window.location.href = data.redirect_url;
                alert(data['msg']);
            }
        });
}

function delete_item(str_url){
    console.log(str_url);
    const csrftoken = getCookie('csrftoken');
    var tokens = str_url.split('/');
    console.log(tokens);
    var item_slug = tokens[tokens.length-3];

    console.log(item_slug);

    $.ajax({
        url : str_url,
        type : 'POST',
        headers : {'X-CSRFToken' : csrftoken},
        data : {'item_slug' : item_slug},
        success: function (data){

            setTimeout(function(){
                location.reload();
            }, 1500);

        }
    });
}
function subscribe_to_proposal(){
    console.log("you pressed subs button")
    // get the user - same way as in get user ajax function
    console.log("getting user")
        const username = $("#profile-link").attr("username-data");
        const btn = $("#subscribe-btn");
        const url = btn.attr("data-url-action");
        console.log("printing url of request");
        console.log(url);

        const proposal_slug = btn.attr("data-prop-slug");
         $.ajax({
             //type : "POST",
             url : url,
             data : {'username': username, 'proposal_slug':proposal_slug },
             success : function(data){

                 console.log(this);
                 if (btn.attr("value") === "Unsubscribe") {
                     btn.html("Subscribe");
                     btn.attr("value", "Subscribe");
                     btn.attr("data-url-action","/sharespace/ajax/sub_proposal/");
                 }else{
                     btn.html("Unsubscribe");
                     btn.attr("value", "Unsubscribe");
                     btn.attr("data-url-action","/sharespace/ajax/unsub_proposal/");
                 }
                 console.log("updating subs count:");
                 $('#subs-count').html(data.subs_count);
                 $('#price-per-person').html(data.price_per_person);
                 console.log("subs request complete");
                 location.reload();

            }
        });


}

function comment_proposal(proposal_slug){

    const url = $('#post-comment-btn').attr('btn-data');
    const comment_text = $('#proposal-comment').val();
    const csrftoken = getCookie('csrftoken');
    console.log(comment_text)

    $.ajax({
        url : url,
        type : 'POST',
        headers : {'X-CSRFToken' : csrftoken},
        data : {'prop_slug': proposal_slug,
                'comment_text': comment_text},
        success: function (data){
            console.log(data);
            let elem = document.createElement("div");
            elem.setAttribute("class", "d-flex gap-2 w-100 justify-content-between");
            elem.innerHTML = data;
            let comment_section = document.getElementById("comment-list")
            comment_section.append(elem);
            let comment= $('#proposal-comment')
            comment.text("");
            comment.val("");

        }
    });
}

function delete_purchase_proposal(prop_slug){
    console.log("request for deleting purchase proposal");
    const csrftoken = getCookie('csrftoken');
    const url = $('#delete-prop-btn').attr('btn-data');
    console.log(prop_slug)

    $.ajax({
        url : url,
        type : 'POST',
        headers : {'X-CSRFToken' : csrftoken},
        data :{
            'prop_slug': prop_slug
        },
        success: function (data){
            console.log(data);
            window.location.href = data['redirect_url'];
            alert(data['msg']);
        }
    });


}

function confirm_item_pick_up(loan_slug){
    console.log("in confirm item pick up function");
    const csrftoken = getCookie('csrftoken');
    let btn = $('#confirm-pickup-btn');
    const url = btn.attr('data-ajax-url');
    console.log(url)

    $.ajax({
        url : url,
        type : 'POST',
        headers : {'X-CSRFToken' : csrftoken},
        data :{
            'loan_slug': loan_slug
        },
        success: function (data){

            location.reload();
            alert(data)
        }
    });


}