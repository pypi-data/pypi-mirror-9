var RecaptchaOptions = {
    theme : 'white'
 };

function renderCurrentYear() {
	var mydate=new Date()
	var year=mydate.getYear()
	if (year < 1000)
	year+=1900
	var day=mydate.getDay()
	var month=mydate.getMonth()
	var daym=mydate.getDate()
	if (daym<10)
	daym="0"+daym
	document.write(year)
}

function toggle(source, name) {
  checkboxes = document.getElementsByName(name);
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}