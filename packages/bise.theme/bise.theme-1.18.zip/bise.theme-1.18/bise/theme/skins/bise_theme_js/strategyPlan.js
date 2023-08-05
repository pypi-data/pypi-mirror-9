	var totalHeight = 720;
	var totalWidth = 930;
	$(function() {
		$(".actionsDiv").css("cursor", "pointer");
		$(".targetId").css("cursor", "pointer");
		$(".targetId").click(function(){
			if (!$(this).parent().hasClass("expanded")){
				$(".targetId").css("cursor", "auto");

				showBackBar($(this).parent());

				$(".targetDiv").toggleClass("collapsed");
		  		$(this).parent().toggleClass("collapsed");
		  		$(this).parent().toggleClass("expanded");  

	  			$(".indicatorsDiv").hide();
	  			$(".cifGroupsDiv").hide();
	  			$(".actionsDiv").hide();
	  			$(".aichiTargetsDiv").hide();	
	  			
	  			$(this).parent().find(".targetDesc").css("width", totalWidth);
	  			$(this).parent().find(".targetDesc").css("height", totalHeight - 120);
	  			$(this).parent().find(".targetDesc").show();
	  		}
		});
  		$(".actionsDiv").click(function(){
  			if (!$(this).parent().hasClass("expanded")){
  				$(".targetId").css("cursor", "auto");

				$(".actionsDiv").css("cursor", "auto");

				showBackBar($(this).parent());

	  			$(".targetDiv").toggleClass("collapsed");
	  			$(this).parent().toggleClass("collapsed");
	  			$(this).parent().toggleClass("expanded");  
	  			$(".targetDesc").hide();
	  			$(".indicatorsDiv").hide();
	  			$(".cifGroupsDiv").hide();
	  			$(".actionsDiv").hide();
	  			$(".aichiTargetsDiv").hide();

	  			$(this).show();
	  			$(this).children().first().hide();
	  			$(this).css("height", (totalHeight - 120));
	  			$(this).parent().find(".action").show();
	  			$(this).parent().find(".action").css("width", totalWidth);
	  			var actionCount = $(this).children().length - 1;
	  			var actionHeight = (totalHeight - 120) / actionCount;
	  			$(this).parent().find(".action").css("height", actionHeight);
	  			$(this).parent().find(".actionDesc").show();


	  			/**$(".targetsBack").css("height", "20px");

	  			$(".targetDiv").toggleClass("collapsed");
	  			$(this).parent().toggleClass("collapsed");
	  			$(this).parent().toggleClass("expanded");  
	  			$(".indicatorsDiv").hide();
	  			$(".cifGroupsDiv").hide();
	  			$(".aichiTargetsDiv").hide();
	  			$(".actionsDiv").hide();

	  			$(this).show();	
	  			$(this).children().first().hide();
	  			$(this).css("height", (totalHeight - 270));
	  			$(this).parent().find(".action").show();
	  			$(this).parent().find(".action").css("width", totalWidth);

	  			var actionCount = $(this).children().length - 1;
	  			var actionHeight = (totalHeight - 270) / actionCount;
	  			$(this).parent().find(".action").css("height", actionHeight);
	  			$(this).parent().find(".action").css("padding-top", (actionHeight/2)-10);*/
	  		}
  		});
  		/**$('body').on('click', '.expanded .action', function () {
  			if (!$(this).parent().parent().hasClass("actionsExpanded")){
	  			$(".actionBack").css("height", "40px")
	  			//$(".actionBack").removeClass().addClass("actionBack").addClass("target2Bg");
	  			//$(this).parent().parent().find(".targetId").hide();
	     		//$(this).parent().parent().find(".targetDesc").hide();
	  			var actionCount = $(this).siblings().length;
	  			var actionHeight = (totalHeight - 40) / actionCount;
	  			$(this).parent().find(".action").css("height", actionHeight);
	  			$(this).parent().find(".action").css("padding-top", "10px");
	  			$(this).parent().find(".action").css("cursor", "auto");
	  			$(this).parent().css("margin-top", "40px");
	  			$(this).parent().css("height", "100%");
	  			$(this).parent().find(".actionDesc").show();
	  			$(this).parent().parent().toggleClass("actionsExpanded");
	  		}
		});*/
		$(".actionBack").css("cursor", "pointer");
		$(".actionBack").click(function(){
			hideBackBar();
  			//$(".targetId").show();
     		//$(".targetDesc").show();	
     		$(".actionDesc").hide();	
     		
			$(".actionsExpanded").find(".actionsDiv").css("margin-top", "0px");
     		var actionCount = $(".actionsExpanded").find(".actionsDiv").children().length - 1;
     		var actionHeight = (totalHeight - 270) / actionCount;
     		$(".actionsExpanded").find(".action").css("height", actionHeight);
     		$(".actionsExpanded").find(".action").css("cursor", "pointer");
     		$(".actionsExpanded").find(".action").css("padding-top", (actionHeight/2)-10);

     		$(".targetDiv").removeClass("actionsExpanded");	
		});		
  		$(".targetsBack").css("cursor", "pointer");
  		$(".targetsBack").click(function(){
  			hideBackBar();

  			$(".actionBack").css("height", "0px")
  			//$(".targetId").show();
  			//$(".targetId").css("height", "270px")
     		//$(".targetDesc").hide();

  			$(".targetDiv").removeClass("collapsed");
  			$(".targetDiv").removeClass("expanded");
  			$(".targetDiv").removeClass("actionsExpanded");

			$(".targetDesc").hide();

			var divHeight = (totalHeight - 270) / 4;

			$(".targetId").css("cursor", "pointer");

  			$(".actionsDiv").show();
  			$(".actionsDiv").css("cursor", "pointer");
  			$(".actionsDiv").css("height", divHeight);
  			$(".actionsDiv").css("margin-top", "0px");
  			$(".actionsDiv").children().hide();
			$(".actionsDiv > div:first-child").show();

			$(".actionDesc").hide();
			
  			$(".indicatorsDiv").show();
  			$(".indicatorsDiv").css("cursor", "pointer");
  			$(".indicatorsDiv").css("height", divHeight);
  			$(".indicatorsDiv").children().hide();
			$(".indicatorsDiv > div:first-child").show();

  			$(".cifGroupsDiv").show();
  			$(".cifGroupsDiv").css("cursor", "pointer");
  			$(".cifGroupsDiv").css("height", divHeight);
  			$(".cifGroupsDiv").children().hide();
			$(".cifGroupsDiv > div:first-child").show();

  			$(".aichiTargetsDiv").show();
  			$(".aichiTargetsDiv").css("cursor", "pointer");
  			$(".aichiTargetsDiv").css("height", divHeight);
  			$(".aichiTargetsDiv").children().hide();
			$(".aichiTargetsDiv > div:first-child").show();  			
  		});

  		$(".cifGroupsDiv").css("cursor", "pointer");
  		$(".cifGroupsDiv").click(function(){
  			if (!$(this).parent().hasClass("expanded")){
  				$(".targetId").css("cursor", "auto");
				$(".cifGroupsDiv").css("cursor", "auto");

	  			showBackBar($(this).parent());

	  			$(".targetDiv").toggleClass("collapsed");
	  			$(this).parent().toggleClass("collapsed");
	  			$(this).parent().toggleClass("expanded");  
	  			$(".targetDesc").hide();
	  			$(".actionsDiv").hide();
	  			$(".indicatorsDiv").hide();
	  			$(".aichiTargetsDiv").hide();  		
	  			$(".cifGroupsDiv").hide();

	  			$(this).show();	
	  			$(this).children().first().hide();
	  			$(this).css("height", (totalHeight - 120));	
	  			$(this).parent().find(".cifGroup").show();
	  			$(this).parent().find(".cifGroup").css("width", totalWidth);
	  			var indicatorHeight = (totalHeight - 120);
	  			$(this).parent().find(".action").css("height", indicatorHeight);  	
	  		}		
  		});

  		$(".indicatorsDiv").css("cursor", "pointer");
  		$(".indicatorsDiv").click(function(){
  			if (!$(this).parent().hasClass("expanded")){
  				$(".targetId").css("cursor", "auto");
				$(".indicatorsDiv").css("cursor", "auto");

	  			showBackBar($(this).parent());

	  			$(".targetDiv").toggleClass("collapsed");
	  			$(this).parent().toggleClass("collapsed");
	  			$(this).parent().toggleClass("expanded");  
	  			$(".targetDesc").hide();
	  			$(".actionsDiv").hide();
	  			$(".cifGroupsDiv").hide();
	  			$(".aichiTargetsDiv").hide();  		
	  			$(".indicatorsDiv").hide();

	  			$(this).show();	
	  			$(this).children().first().hide();
	  			$(this).css("height", (totalHeight - 120));	
	  			$(this).parent().find(".indicator").show();
	  			$(this).parent().find(".indicator").css("width", totalWidth);
	  			var indicatorHeight = (totalHeight - 120);
	  			$(this).parent().find(".action").css("height", indicatorHeight);  	
	  		}		
  		});
  		$(".aichiTargetsDiv").css("cursor", "pointer");
  		$(".aichiTargetsDiv").click(function(){
  			if (!$(this).parent().hasClass("expanded")){
  				$(".targetId").css("cursor", "auto");
				$(".aichiTargetsDiv").css("cursor", "auto");

				showBackBar($(this).parent());

	  			$(".targetDiv").toggleClass("collapsed");
	  			$(this).parent().toggleClass("collapsed");
	  			$(this).parent().toggleClass("expanded");  
	  			$(".targetDesc").hide();
	  			$(".indicatorsDiv").hide();
	  			$(".cifGroupsDiv").hide();
	  			$(".actionsDiv").hide();
	  			$(".aichiTargetsDiv").hide();

	  			$(this).show();
	  			$(this).children().first().hide();
	  			$(this).css("height", (totalHeight - 120));
	  			$(this).parent().find(".aichiTarget").show();
	  			$(this).parent().find(".aichiTarget").css("width", totalWidth);
	  			var aichiTargetCount = $(this).children().length - 1;
	  			var aichiTargetHeight = (totalHeight - 120) / aichiTargetCount;
	  			$(this).parent().find(".aichiTarget").css("height", aichiTargetHeight);
	  		}
  		});  	
  		function showBackBar(target)	{
  			$(".targetsBack").show();
			$(".targetsBack").css("height", "25px");
			if (target.hasClass("target1Bg")){
				$(".targetsBack").addClass("target1Backbg");
			}else if (target.hasClass("target2Bg")){
				$(".targetsBack").addClass("target2Backbg");
			}else if (target.hasClass("target3Bg")){
				$(".targetsBack").addClass("target3Backbg");
			}else if (target.hasClass("target4Bg")){
				$(".targetsBack").addClass("target4Backbg");
			}else if (target.hasClass("target5Bg")){
				$(".targetsBack").addClass("target5Backbg");
			}else if (target.hasClass("target6Bg")){
				$(".targetsBack").addClass("target6Backbg");
			}
  		}
  		function hideBackBar(){
  			$(".targetsBack").hide();
  			$(".targetsBack").css("height", "0px");
  			$(".targetsBack").removeClass("target1Backbg");
			$(".targetsBack").removeClass("target2Backbg");
			$(".targetsBack").removeClass("target3Backbg");
			$(".targetsBack").removeClass("target4Backbg");
			$(".targetsBack").removeClass("target5Backbg");
			$(".targetsBack").removeClass("target6Backbg");
  		}
	});
