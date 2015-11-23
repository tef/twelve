========
 twelve 
========
:Author: tef
:Date: 2015-11-23
:Version: 0.1

twelve is a type-length-value encoding that aims to be

- endian independent
- straight forward to implement
- allow human inspection

.. contents::


requirements
============

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in [RFC2119].

data model
==========

twelve natively handles a variety of literals (strings, bytes, 
numbers, floats, utc datetimes, timedeltas, booleans), 
and collections (list, set, dict).  ::

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

twelve also supports special data types:

- an 'extension' type used to define objects with special behaviour or meaning
- a 'blob' used to embed data

top level
---------

a twelve encoded message consists of a single object
	
	root :== ws object ws
	
	ws :== (space | tab | vtab | cr | lf)*
	
	object :== integer | unicode | bytearray | float
		| datetime | timedelta
		| nil | true | false
		| list | set | dict | ordered_dict
		| extension | blob


integer
-------

integers of arbitrary precision, sign is optional, and either '+' or '-'

::
	
	integer :== 'i' sign ascii_number ';'
	sign :== '+' | '-' | ''
	ascii_number :== <a decimal number as an ascii string>
	
	number	encoded:
	123	i123; i+000123;
	-123	i-123;
	0	i0; i-0; i+0;

note: if the decoder cannot represent the number without overflow, 
it SHOULD throw an error

encoders MUST NOT produce numbers with leading 0s. decoders MUST
ignore leading zeros.

unicode
-------

a unicode element is a utf-8 encoded string. MUST NOT include
utf-16 surrogate pairs. Modified UTF-8/CESU-8 MUST NOT be used.

..
	(JSON, Java, I'm looking at *you*)

::

	unicode :== 'u' ascii_number ':' utf8_bytes ';' | empty_unicode
		where len(bytes) = int(ascii_number)
	
	empty_unicode :== 'u;'

	utf8_bytes :== <the utf8 string>

	string 	encoding
	''	u;
	'foo'	u3:foo;
	'bar'	u4:bar;
	'💩'	u4:\xf0\x9f\x92\xa9;

	n.b length is length of bytes, not length of string

Encoders SHOULD normalize strings to NFC, decoders MAY
normalize strings to NFC.

unicode should map to the native string type where applicable.


bytearray
---------

a byte array is a string of bytes. no encoding
is assumed, i.e, an octet-stream.

::

	bytearray :== 'b' ascii_number ':' bytes ';' | empty_bytearray
		where len(bytes) = int(ascii_number)

	empty_bytearray = 'b;'

	bytes			encoding
	[0x31,0x32,0x33]	b3:123;
	[]			b;


singletons
----------

twelve has three singleton types: true, false, and nil::

	true :== 'T;'
	false :== 'F;'
	nil :== 'N;'

nil SHOULD map to null or None or nil.

collections
-----------

twelve has four collection types, an ordered list,
an unordered set, and an ordered & unordered dictionary.

sets and dicts MUST NOT have duplicate items,
clients SHOULD not recover.

::

	list :== 'L' ws (object ws)* ';'
	set :== 'S' ws (object ws)* ';'
	dict :== 'D' ws (object ws object ws)* ';'
	ordered_dict :== 'O' ws (object ws object ws)* ';'

	object			encoding

	list(1,2,3)		Li1;i2;i3;;
	set(1,2,3)		Si1;i2;i3;;
	dict(1:2, 3:4)		Di1;i2;i3;i4;;
	ordered_dict(1:2, 3:4)	Oi1;i2;i3;i4;;

lists, ordered_dicts MUST preserve ordering. dicts, sets have no ordering.

datetime
--------

datetimes MUST be in UTC, and MUST be in the following subset of iso-8601/rfc3339 format::

	datetime :== 'd' iso_datetime ';'
	iso_datetime :== <date: %Y-%m-%dT%H:%M:%S.%fZ>

	object		encoding

	1970-1-1	d1970-01-01T00:00:00.000Z;

encoders and decoders MUST support the 'Z' timezone (UTC), but MAY support other offsets.
encoders and decodes SHOULD not strip or ignore timestamps, or convert them.
by default.

timedelta
---------

timedeltas MUST be in the following subset of iso-8601 period format::

	timedelta :== 'p' iso_period ';'
	iso_period :== <period:  pnYnMnDTnHnMnS>

	object			encoding

	3 days, 2 hours		pP0Y0M3DT0H2M0S;

encoders MUST present all leading 0s.

float
-----

floating point numbers can be represented in decimal or
hexadecimal. hexadecimal floats were introduced by C99,
and provide a way for accurate, endian free 
representation of floats. for example::


	float	hex			decimal

	0.5	0x1.0p-1		f0.5;
	-0.5 	-0x1.0p-1 		f-0.5;
	+0.0	0x0p0			f+0.0;
	-0.0	-0x0p0			f-0.0;
	1.729	0x1.ba9fbe76c8b44p+0	f1.729;

hex floats are `<sign.?>0x<hex>.<hex>e<sign><decimal>`, where
the first number is the fractional part in hex, and the latter is the exponent
in decimal.  details on the encoding and decoding of hex floats is covered in an appendix.

twelve uses hex or decimal floats, except for the special floating
point values: nan and infinity::

	float :== 'f' hex_float ';' | 'f' decimal_float ';' | 'f' named_float ';'

	float		encoding	
	0.5		f0x1.0p-1; 	or	f0.5;
	-0.5 		f-0x1.0p-1; 	or 	f-0.5;
	0.0		f0x0p0;		or 	f0.0;

	Infinity	finf; 	or 	fInf;
	-Infinity	f-inf; 	or 	f-inf;
	NaN		fnan; 	or 	fNaN;

decoders MUST ignore case.

encoders MUST use 'inf' or 'Inf', not 'infinity', 'Infinity', etc.

decoders MUST support hex and decimal floats. 

encoders SHOULD use hex floats instead of decimal.


blob
----

binary data can be embedded inside an object

::


	blob :== 'B' id_num ':' attr_dict (':' ascii_number ':' bytes)* ';' 
	note : where len(bytes) = int(ascii_number)

attributes MUST be a dictionary:

- MUST have the key 'content-type'
- MAY have the key 'url'

a server SHOULD transform a response of a solitary blob object into a 
http response, using the content-type attribute.

twelve clients SHOULD return an response with an unknown encoding as a blob,
and SHOULD set the url attribute of the blob object.

the blob is represented by a number of length prefixed chunk of bytes

extensions
----------

extensions are name, attr, content tuples, used internally within twelve
to describe objects with special handling or meaning, rather than
application meaning.

name SHOULD be a unicode string, attributes SHOULD be a dictionary or ordered dictionary::

	extension :== 'X' ws name_obj ws attr_obj ws content_obj ws ';' 
	name_obj :== unicode
	attr_obj :== dict | ordered_dict
	content_obj :== object


extensions
==========

reserved extensions
-------------------

the following extension names are reserved, and should not be used for 
application or vendor specific features::

	typedef, class, method, interface, type
	integer, unicode, string, bytearray, float, datetime,
	timedelta, period, nil, true, false, list, set, dict, 
	ordered_dict, extension, blob, bool, 	
	resource, request, response, error, 
	link, input, form, url


appendix
========

grammar
-------

::

	root :== ws object ws

	ws :== (space | tab | vtab | cr | lf)*

	object :== 
		  integer
		| unicode
		| bytearray
		| float
		| datetime
		| timedelta
		| nil
		| true
		| false
		| list
		| set
		| dict
		| ordered_dict
		| extension
		| blob


	integer :== 'i' sign ascii_number ';'

	unicode :== 'u' ascii_number ':' utf8_bytes ';' 
	            | empty_unicode
	  note: where len(bytes) = int(ascii_number)

	empty_unicode :=='u;'

	bytearray :== 'b' ascii_number ':' bytes ';' 
	              | empty_bytearray
	    note: where len(bytes) = int(ascii_number)

	empty_bytearray = 'b;'

	true :== 'T;'
	false :== 'F;'
	nil :== 'N;'

	list :== 'L' ws (object ws)* ';'
	set :== 'S' ws (object ws)* ';'
	dict :== 'D' ws (object ws object ws)* ';'
	ordered_dict :== 'O' ws (object ws object ws)* ';'

	float :== 'f' hex_float ';'

	datetime :== 'd' iso_datetime ';'
	timedelta :== 'p' iso_period ';'

	extension :== 'X' ws name_obj ws attr_obj ws content_obj ws ';' 
	
	blob :== 'B' id_num ':' attr_dict ':' (ascii_number ':' bytes)* ';' 
	note : where len(bytes) = int(ascii_number)

	end_chunk :== 'c' id_num ';' 

hexadecimal floating point
--------------------------

a hex float has an optional sign, a hex fractional part and a decimal exponent part::
	
	float <optional sign>0x<hex fractional>e<decimal exponent with sign>
	sign is '-','+'
	hex fractional is <leading hexdigits>.<hexdigits> or 0a
	exponent has explicit sign '+'/'-' for numbers other than zero.

many languages support hex floats already::

	language	example

	C99		sprintf("%a",...) 	scanf("%a",...)
	Python		5.0.hex()		float.fromhex('...')
	Java 1.5	Double.toHexString(..)	Double.parseDouble(...)
	ruby 1.9	sprintf("%a", ...) 	scanf("%a", ...)		
	Perl 		Data::Float on CPAN

parsing a float can be done manually, using `ldexp`::


	# convert hhh.fff into a float
	fractional = int(leading,16) + (int(hexdigits,16) / (16**len(hexdigits)))
	# ldexp(f,e) is f + 2**e
	float = sign *  ldexp(fractional, int(exponent))

..
	creating a float can be done manually using `frexp` and `modf`::
		# split the float up
		f,exp = frexp(fractional)
		# turn 0.hhhh->  hhhhh.0 
		f = int(modf(f * 16** float_width)[1])
		# construct hex float
		hexfloat = sign(f) +  '0x0.' hex(abs(f)) + 'p' + signed_exponent

	TODO: fix this, it's broken


changelog
=========

history
-------

twelve started out as a clone of bencoding, which was used
in a rpc framework (hyperglyph)


- 0.0 forked hyperglyph spec 1.0

- 0.1 
  merged chunk, blob objects
  removed http mappings, built in extensions
  extended reserved extensions

planned changes
---------------
- 0.x + 1
  url types, relative url handling
  ascii strings (no NUL, maybe no high bits?)

- 0.x + 2
  typedefs
  typed arrays
  forms, links, resources, collections

- 1.x + 1
  compatibility promise
  human readable (JSON esque format)
  schema/codegen
  on disk encoding (thrift esque for size)
  in mem/on disk encoding (flatbuffers for speed)
