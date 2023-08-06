function refresh_ListingSummaryContent(data){
    // get data from the ajax request and update the Plone content
    foo = $(data).filter('#AjaxFilter');
    if( $(foo).length<1){
        //Server Error?
        foo = '<h2>Ups, something went wrong ... </h2><h3>We are sorry for the troubles. Please try find your property later again.</h3>';
    }

    $('section.listing-summary, .template-listing-detail .listing.detail').replaceWith(foo);
    $('section.listing-summary .js-off').hide();
    $('section.listing-summary .js-on.show').show();
    $('section.listing-summary .js-on.hide').hide();
    //update listing links with search params
    linkMyParams($('.listingLink'));
    linkMyParams($('#portal-breadcrumbs a').last());
    //refresh prepOverlay
    try{
        plonePrettyPhoto.enable();
    }
    catch(error){
        
    }
    //Pagination Links
    full_enhance_listingbar();
    $("#AjaxFilter .listingBar a" ).click(function(event){
        event.preventDefault();
        myUrl = $(this).attr('href');
        ajaxLink(myUrl, true);
        return false;
    });
}

function refresh_Content(data, isListingSummary){
    isListingSummary = isListingSummary || false;

    if(isListingSummary){
        foo = $(data).find('section.listing-summary');

        $('section.listing-summary').replaceWith(foo);
        $('section.listing-summary .js-off').hide();
        $('section.listing-summary .js-on.show').show();
        $('section.listing-summary .js-on.hide').hide();
    }
    else{
        foo = $(data).find('#content');
        $('#content-core').replaceWith(foo);

    }
    
    //refresh prepOverlay
    try{
        plonePrettyPhoto.enable();
    }
    catch(error){
        
    }
 
    //standard pagination links
    //not set by ajaxFilter
    if($('#AjaxFilter').length<1){
        full_enhance_listingbar();
        $(".listing-summary' .listingBar a" ).click(function(event){
            event.preventDefault();
            myUrl = $(this).attr('href');
            ajaxLink(myUrl, false);
            return false;
        });
    }
}

function ajaxLink(target, loadListingSummary, isListingSummary){
    loadListingSummary = loadListingSummary || false;
    isListingSummary = isListingSummary || false;
    //rewrite the batch to work with ajax
    $.ajax({
        url : target,
        crossDomain: true,
        success:function(data, textStatus, jqXHR){
            //data: return data from server
            if(loadListingSummary){
                refresh_ListingSummaryContent(data);
            }
            else{
                refresh_Content(data, isListingSummary);
            }
            
        },
        error: function(jqXHR, textStatus, errorThrown){
        }
    });

}

function linkMyParams(link_obj){
    /* preserve the current filter status is a link
       serialize the form
       update the href(s) of the given link object(s)
    */
    var MyParams = "LCMARKER=1&" + $(".aJaXFilter form").serialize();
    
    $(link_obj).each(function( index ) {
        MyUrl = $(this).attr('href');
        
        if (MyUrl.indexOf("?") > 0){
            connector ="&";
        }
        else{
            connector ="?";
        }
     
        if(MyUrl.indexOf("LCMARKER=1") < 1){
            //our params are not set yet
            newUrl = MyUrl + connector + MyParams;
        }
        else{
            //we set this params before and have to replace them
            splitUrl= MyUrl.split('LCMARKER=1&');
            newUrl = splitUrl[0] + MyParams;
        }
        //finally: update Link Url
        $(this).attr('href', newUrl);

        
    });
}

function setPriceBoxes(commander){
    /* Check the form status and set the correct behaviour */
    isSale   = false;
    isRental = false;
    isLot    = false;
    isMixed  = false;

    settings = $(commander).find('input:checked');
    if (settings.length>0){
        isEmpty = false;
    }
    else{
        isEmpty = true;
    }
        
    if (isEmpty === false){
        //only when we have selected options
        settings.each(function(index) {
            //classify search request with the set options
            switch ($(this).val())
            {
                case 'rental':  isRental= true;
                                break;
                case 'sale':    isSale= true;
                                break;
                case 'lot':     isSale= true;
                                isLot= true;
                                break;
                default:        break;
            }

        });
        if(isSale && isRental){
            isMixed     = true;
            isSale      = false;
            isRental    = false;
        }
        else{
            isMixed     = false;
        }

        if(isLot){
            //for Lots: hide pool and beds
            collapseMe('#formfield-form-widgets-pool');
            collapseMe('#formfield-form-widgets-beds');
            $('#formfield-form-widgets-pool, #formfield-form-widgets-beds').fadeOut();
        }
        else{
            $('#formfield-form-widgets-pool, #formfield-form-widgets-beds').fadeIn();
        }

        if(isMixed){
            // close sales & rent price ranges
            collapseMe('#formfield-form-widgets-price_sale');
            collapseMe('#formfield-form-widgets-price_rent');
            $('#formfield-form-widgets-price_sale, #formfield-form-widgets-price_rent').fadeOut();
        }
        else{
            if(isSale){
                // close rent price ranges & mixed limit
                collapseMe('#formfield-form-widgets-price_rent');
                $('#formfield-form-widgets-price_rent').fadeOut();
                //open sales price range
                $('#formfield-form-widgets-price_sale').fadeIn();
                openMe('#formfield-form-widgets-price_sale');
            }
            if(isRental){
                // close sales price ranges & mixed limit
                collapseMe('#formfield-form-widgets-price_sale');
                $('#formfield-form-widgets-price_sale').fadeOut();
                //open rental price range
                $('#formfield-form-widgets-price_rent').fadeIn();
                openMe('#formfield-form-widgets-price_rent');
            }
        }

    }
    if(isEmpty){
        // close all
        collapseMe('#formfield-form-widgets-price_rent');
        collapseMe('#formfield-form-widgets-price_sale');
        $('#formfield-form-widgets-price_sale, #formfield-form-widgets-price_rent').fadeOut();
        $('#formfield-form-widgets-pool, #formfield-form-widgets-beds').fadeIn();
    }
}

function collapseMe(field_id) {
        var indicator   = $(field_id).find('.collapser:first');
        var target      = $(field_id).find('.collapse:first');
            
        target.slideUp('normal');
        indicator.removeClass('expanded');
        indicator.addClass('collapsed');
        
}

function openMe(field_id) {
        var indicator   = $(field_id).find('.collapser:first');
        var target      = $(field_id).find('.collapse:first');
        
        target.slideDown('normal');
        indicator.addClass('expanded');
        indicator.removeClass('collapsed');
}

function stateChecker(field_id, field_type){
    field_type  = field_type || "checkbox";
    openField = false;
    closeField = false;
   
    var commander   = $(field_id);
    var indicator   = $(field_id).find('.collapser:first');
    var target      = $(field_id).find('.collapse:first');

    switch(field_type){
        case 'checkbox':
            settings = $(commander).find('input:checked');
            if (settings.length>0){
                //we have a checked checkbox
                openField  = true;
                closeField = false;
            }else{
                //nothing set
                openField  = false;
                closeField = true;
            }
            break;
        case 'radio':
            settings = $(commander).find('input:checked');
            if (settings.length>0 && settings.val()!=='--NOVALUE--'){
                //we have a checked radio button
                //lets check its value
                openField  = true;
                closeField = false;
            }else{
                //nothing set
                openField  = false;
                closeField = true;
            }
            break;
        case 'text': break;
        default: break;
    }
    if(openField){
        openMe(field_id);
    }
    if(closeField){
        collapseMe(field_id);
    }

}

function setContentAsCSSclass(options){
  /*set the value of the fields as css class to the option*/
  $(options).each(function( index ) {
    myClass="class_" + $(this).find('input').val();
    $(this).addClass(myClass);
    });

}

function full_enhance_listingbar(){
    //remove the ugly [ 1 ] notation and give it a class
    $('.listingBar').html(function(i,html){
        foo = html.replace('[','<span class="active">').replace(']','</span>');
        return foo;
    });
    $(".listingBar .next a" ).text('>>');
    $(".listingBar .previous a").text('<<');
}

/*Incluse Mapplic JS*/
function mapplic_hash(){
    // set page id also as hash value
    // needed for Mapplic deeplinking
    foo = location.pathname.split('/');
    id =foo[foo.length-1];
    location.hash=id;
}

function unhash_link(links){
  //replace hash links to real links
  $(links).each(function( index ) {

    href_o = $(this).attr('href').replace('#','');
    foo = location.pathname.split('/');
    last = foo.length-1;
    foo[last]=href_o;
    href_n= foo.join('/');

    $(this).attr('href', href_n);
  });
  
}

function reset_link_show(){
    //if reset link don't exist, add it to the end of the form
    if ($('.aJaXFilter form .reset').length<1){
        $('.aJaXFilter form').append('<span class="reset ajax_reset">Clear Filter</span>');
    }
    else{
        $('.aJaXFilter form .reset').show();
    }
    $('.aJaXFilter form .reset').off("click");
    $('.aJaXFilter form .reset').click(function(event){
        event.preventDefault();
        reset_ajaxform();
        return false;
    });

}

function reset_link_hide(){
    $('.aJaXFilter form .reset').hide();
}

function switch_Reset(){
    //if any checkbox/ radion button is active show Link
    if($(".aJaXFilter form input:checked").not('#form-widgets-pool-2').length>0){
        reset_link_show();
    }
    //else hide it
    else{
        reset_link_hide();
    }
}

function searchUrl(){
    SearchPath=$(".aJaXFilter form").attr('action');
    pathArray = SearchPath.split('@@');
    return pathArray[0];
}

function reset_ajaxform(){
    window.location.href=searchUrl();
}

function clearQueue(){
    request_count= AjaxQueue.length;

    for (var i = 0; i < request_count; i++) {
        stopper=AjaxQueue.pop();
        stopper.abort();
    }
}

function back2Results(header){
    myUrl= searchUrl();
    $(header).html('<a class="back2results" href="'+myUrl+'"">Back to Results</a>');
    linkMyParams($('a.back2results'));
}

function short_info(){
 //use data input to give back a easy to access array for mapping
  dict=[];

  if($('dl.price dd').length>0){
    dict.price= $('dl.price dd').html();
  }else{dict.price=null;}
  
  if($('#listing-info dd.object_type').length>0){
    dict.propertytype= $('#listing-info dd.object_type').html();
  }else{dict.propertytype=null;}
  
  if($('#listing-info dd.beds_baths').length>0){
    dict.bed_bath= $('#listing-info dd.beds_baths').html();
  }else{dict.bed_bath=null;}

  if($('#listing-info dd.lot_size').length>0){
    dict.lotsize= $('#listing-info dd.lot_size').html();
  }else{dict.lotsize=null;}
  
  if($('#listing-details .living_area td').length>0){
        dict.lotsize= $('#listing-details .living_area td').html();
  }
  
  pool_text = $(".pool_meta td").html();
  if(pool_text !='No'){
      pool_text ='Yes';
  }
  dict.pool= pool_text;

  seperator='&nbsp;&nbsp;|&nbsp;&nbsp;';
  html_string = '<div class="short_info">';
  if(dict.propertytype!==null){
      html_string += '<div class="float_left"><span class="label type"><b>TYPE</b>&nbsp;&nbsp;</span><span class="value type">'+dict.propertytype+seperator+'</span></div>';
  }
  if(dict.bed_bath!==null){
      html_string += '<div class="float_left"><span class="label bed_bath"><b>BED/ BATH</b>&nbsp;&nbsp;</span><span class="value bed_bath">'+dict.bed_bath+seperator+'</span></div>';
  }
  if(dict.lotsize!==null){
      html_string += '<div class="float_left"><span class="label size"><b>SIZE</b>&nbsp;&nbsp;</span><span class="value size">'+dict.lotsize+seperator+'</span></div>';
  }
  if(dict.price!==null){
    seperator='';
    html_string += '<div class="float_left"><span class="label price"><b>PRICE</b>&nbsp;&nbsp;</span><span class="value price">'+dict.price+seperator+'</span></div>';
  }

  html_string += '</div>';
  
  $("#listing-info").before(html_string);
  $("#listing-info").hide();
  return true;
}

var AjaxQueue = [];

$(document).ready(function() {
    //if the AjaxFilter Portlet is available
    // execute the AjaxSearch
    if($('.aJaXFilter').length>0){

        $(".aJaXFilter form").submit(function(e){
            e.preventDefault(); //STOP default action

            var formURL = $(this).attr("action");
            //stop active ajax calls
            clearQueue();
            
            if($('.template-listing-detail').length<1){
                //if we are not on listing details
                // send ajax request
                var postData = $(this).serializeArray();
                
                var caller = $.ajax({
                    url : formURL,
                    type: "POST",
                    crossDomain: false,
                    data : postData,
                    success:function(data, textStatus, jqXHR){
                        //data: return data from server
                        refresh_ListingSummaryContent(data);

                    },
                    error: function(jqXHR, textStatus, errorThrown){
                        //if fails   
                    }
                });

                AjaxQueue.push(caller);

            }
            else{
                splitUrl = formURL.split('@@');
                newUrl   = splitUrl[0] + "?LCMARKER=1&" + $(this).serialize();
                window.location.href = newUrl;
            }
            
        });

        //improve the form classes
        setContentAsCSSclass($('.aJaXFilter span.option'));

        //Improve Display for ListingDetails
        if($('.template-listing-detail').length>0){
            back2Results($('.aJaXFilter .portletHeader'));
            short_info();
        }
        
        //submit searchform to show results of preserved search?
        if($('section.listing-summary').length>0 && window.location.href.indexOf("LCMARKER=1") > 0){
          switch_Reset();
          $(".aJaXFilter form").submit();
        }

        //add change event to form fields
        // no submit button needed
        $(".aJaXFilter input").change(function(){
            switch_Reset();
            $(".aJaXFilter form").submit();
        });
        
        $(".aJaXFilter form").on('reset', function(e){
            switch_Reset();
            // update results after form reset
        });

        // add UI Price improvements
        $(".aJaXFilter #formfield-form-widgets-listing_type").change(function(){
            setPriceBoxes(this);
        });

        //unset default Plone classes
        $('.aJaXFilter form').removeClass();

        //standard setup: field expanded if value is set inside
        //stateChecker('#formfield-form-widgets-listing_type');
        switch_Reset();
        openMe('#formfield-form-widgets-listing_type');
        stateChecker('#formfield-form-widgets-beds', 'radio');
        stateChecker('#formfield-form-widgets-view_type');
        stateChecker('#formfield-form-widgets-pool', 'radio');
        //set price display
        setPriceBoxes('#formfield-form-widgets-listing_type');

        //"remember" form status in links
        linkMyParams($('.listingLink'));
        linkMyParams($('#portal-breadcrumbs a').last());
        linkMyParams($('.relatedProperties a.listing_link'));
  
    }
});
