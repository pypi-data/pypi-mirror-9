function column_equalizer(){
    // Equalize content text columns to the same height
    $('.equal-heights').equalize({children: '.equalized-item', reset: true, breakpoint: 750});
    return;
}

$(document).ready(function($) {
    /*
    * Button dropdown trick
    */
    // We can't use "data-***" html5 attibutes with ckeditor, but Foundation5 
    // requires them for Button Dropdown, so we add them on the fly for these 
    // buttons that have the "trick" class. Also their "id" is automatically 
    // added so you don't have to manage them.
    $('a.button.dropdown.trick').each(function( index ) {
        var dropdown_id = "dropdown-trick-"+index,
            dropdown_menu,
            container;
        if( $( this ).parent().get(0).tagName == 'P' || $( this ).parent().get(0).tagName == 'LI' ) {
            container = $(this).parent();
        } else {
            container = $(this);
        }
        dropdown_menu = container.next("ul.f-dropdown");
        if(dropdown_menu){
            $(this).attr('data-dropdown', dropdown_id);
            dropdown_menu.attr('id', dropdown_id).attr('data-dropdown-content', '');
        }
    });
    
    /* 
     * Apply the trick to swap <img> elements into their container background
     */
    $('img.background').swapImageToBackground();
    
    /*
    * Conditionnal contents loading from interchange being
    */
    $interchanged_content_intro = $('#interchanged-content-intro');
    if($interchanged_content_intro.length>0){
        // Triggered event when Foundation 'interchange' plugin replace the content
        $interchanged_content_intro.on('replace', function (e, new_path, original_path) {
            $('#slideshow-container').foundation('orbit');
        });
        // Fallback for small resolution which is excluded from the interchange content 
        // (and so does not trigger a 'replace')
        if(matchMedia(Foundation.media_queries.small).matches){
            $('#slideshow-container').foundation('orbit');
        }
        
    } else {
        // Last fallback if there is no interchange content
        // ...
    }
    
    /*
    $(window).load(function () {
        // Equalize some columns after full page loading
        // NOTE: Needed to be in the $.load(), because webkit raise ready() even if it does not have 
        //       downloaded all ressources, this cause false dimensions because all images 
        //       have not yet be downloaded, so they doesn't set true dimensions on their 
        //       parent and etc..
        column_equalizer();

    });
    $(window).resize(function() {
        column_equalizer();
    });
    */
    
    /*
    * Initialize Foundation after all event is binded
    */
    $(document).foundation();

});
