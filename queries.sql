
.print "get username,password"
select password,username from accounts where username="student1";

.print "getting student1's marks"
select a1,a2,a3,midterm,final,lab from marks
    where utorid = 'student1';

.print "create remarking request"
insert into remarks values("student1","reason",true,true,true,true,true,true);

.print "create feedback"
insert into feedback values("instructor1","I like x","I want you to do y","I like labs","I want labs to improve");

.print "Get list of instructors"
select utorid from accounts where instructor=true;

.print "Get feedback for a instructor"

select likeinstructor, improveinstructor, likelabs, improvelabs from feedback where instructorid = "instructor1";

.print "getting all student's marks(instructor)"
select utorid, a1,a2,a3,midterm,final,lab from marks;

.print "Update marks for user"

update marks set a1=100, a2=100, a3=100, midterm=100, final=100, lab=100 where utorid = 'student1';

.print "get remark requests"

select reason, a1,a2,a3,midterm,lab,final from remarks;
