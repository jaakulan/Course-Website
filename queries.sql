.print "getting all student's marks(instructor)"
select a1,a2,a3,midterm,final,lab from marks;

.print "getting student1's marks"
select a1,a2,a3,midterm,final,lab from marks
    where utorid == 'student1';
