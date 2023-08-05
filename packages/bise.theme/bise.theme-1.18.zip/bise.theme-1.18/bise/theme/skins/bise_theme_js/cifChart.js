      var level2Opened = true;
      var level3Opened = true;
      var level4Opened = true;
      var level5Opened = true;
      $(function() {


        //$('*[data-level="L2"]').hide();
        //$('*[data-level="L3"]').hide();
        //$('*[data-level="L4"]').hide();
        //$('*[data-level="L5"]').hide();
        //$("#showL2").css("cursor", "pointer");
        /**$("#showL2").click(function(e) {
          if(!$(e.target).is('a') ){
            if (!level2Opened){
              showL2();
            }else{
              hideL2();
            };
          }
        });*/

        /**$("#showL3").css("cursor", "pointer");
        $("#showL3").click(function() {
          if (!level3Opened){
            showL3();
          }else{
            hideL3();
          }
        });  */

        $('*[data-show="L4"]').css("cursor", "pointer");
        $('*[data-show="L4"]').click(function() {
          if (!level4Opened){
            showL4();
          }else{
            hideL4();
          }
        });
        //$("#hideL4").click(function() {hideL4();});
        
        $('*[data-show="L5"]').css("cursor", "pointer");     
        $('*[data-show="L5"]').click(function() {
          if (!level5Opened){
            showL5();
            $('*[data-level="L6"]').css("border-top", "0px");
          }else{
            hideL5();
            $('*[data-level="L6"]').css("border-top", "1px solid #E6E6E6");
          }
        });
        //$("#hideL5").click(function() {hideL5();});                    
      });
      /**function showL2(){
        //$('*[data-level="L2"]').slideDown();
        //level2Opened = true;
      }
      function showL3(){       
        $('*[data-level="L3"]').slideDown();
        $('*[data-show="L4"]').css("border-bottom", "1px solid black");
        level3Opened = true;
      }*/
      function showL4(){
        $('*[data-level="L4"]').slideDown();
        $('*[data-show="L4"]').css("border-bottom", "0");
        level4Opened = true;
      }
      function showL5(){     
        $('*[data-level="L5"]').slideDown();  
        level5Opened = true;
      }   

      /**function hideL2(){            
        $('*[data-level="L2"]').slideUp();       
        level2Opened = false;
        $('*[data-level="L3"]').slideUp();       
        level3Opened = false;
        $('*[data-level="L4"]').slideUp();
        level4Opened = false;
        $('*[data-level="L5"]').slideUp();
        level5Opened = false;
      }
      function hideL3(){
        $('*[data-level="L3"]').slideUp();         
        level3Opened = false;
        $('*[data-level="L4"]').slideUp();
        level4Opened = false;
        $('*[data-level="L5"]').slideUp();           
        level5Opened = false;
      }*/
      function hideL4(){       
        $('*[data-level="L4"]').slideUp();
        level4Opened = false;
        $('*[data-level="L5"]').slideUp();
        level5Opened = false;
        $('*[data-show="L4"]').css("border-bottom", "1px solid #E6E6E6");
      }
      function hideL5(){  
        $('*[data-level="L5"]').slideUp();      
        level5Opened = false;
      }  