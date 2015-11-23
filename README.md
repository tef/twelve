# twelve

this is a simple type:length:value esque protocol, derived from bencoding, 
and in turn, netstrings. 

twelve natively handles a variety of literals (strings, bytes, 
numbers, floats, utc datetimes, timedeltas, booleans), 
and collections (list, set, dict).  ::

```
data type		example			encoded

integer			1			i1;
unicode			"hello"			u5:hello;
bytearray		[0x31, 0x32, 0x33]	b3:123;
list			[1,2,3]			Li1;i2;i3;;
set			set(1,2,3)		Si1;i2;i3;;
dict			{1:2, 2:4}		Di1;i2;i3;i4;;
ordered_dict		ordered(1:2, 2:4)	Oi1;i2;i3;i4;;
singleton		nil true false		N; T; F;
float			0.5			f0x1.0p-1;  or f0.5;
datetime		1970-1-1 00:00 UTC	d1970-01-01T00:00:00.000Z;
timedelta		3 days			pP0Y0M3DT0H0M0S;
```

twelve also supports special data types:

- an 'extension' type used to define objects with special behaviour or meaning
- a 'blob' used to embed data

