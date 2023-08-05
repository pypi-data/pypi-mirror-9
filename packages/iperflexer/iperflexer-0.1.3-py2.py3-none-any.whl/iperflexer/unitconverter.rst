The Unit Converter
==================

The unit converter is a table to convert Data Rates.

Unit Names and Constants
------------------------

This has gotten way too long. I should break it up.

Decimal Unit Names
~~~~~~~~~~~~~~~~~~

These are base-10 units. The intention is to use them to convert the iperf (goodput) output so the strings themselves have to match the units iperf uses. Bit to make it easier to remember I'm aliasing them with long-names as well.

.. '

::

    class UnitNames(object):
        """
        Unit Names is a namespace to hold units
        """
        __slots__ = ()
        #bits
        bits = "bits"
        kbits = "K" + bits
        kilobits = kbits   
        mbits = "M" + bits
        megabits = mbits
        gbits = "G" + bits
        gigabits = gbits
        tbits = "T" + bits
        terabits = tbits
        pbits = "P" + bits
        petabits = pbits
        ebits = "E" + bits
        exabits = ebits
        zbits = "Z" + bits
        zettabits = zbits
        ybits = "Y" + bits
        yottabits = ybits
    
        # bytes
        bytes = "Bytes"
        kbytes = "K" + bytes
        kilobytes = kbytes
        mbytes = "M" + bytes
        megabytes = mbytes
        gbytes = "G" + bytes
        gigabytes = gbytes
        tbytes = "T" + bytes
        terabytes = tbytes
        pbytes = "P" + bytes
        petabytes = pbytes    
        ebytes = "E" + bytes
        exabytes = ebytes    
        zbytes = 'Z' + bytes
        zettabytes = zbytes
        ybytes = 'Y' + bytes
        yottabytes = ybytes
    



Binary Unit Names
~~~~~~~~~~~~~~~~~

::

    class BinaryUnitNames(object):
        """
        namespace for binary-unit names
        """
        bits = UnitNames.bits
        bibits = 'bi' + bits
        kibibits = "ki" + bibits
        mebibits = 'me' + bibits
        gibibits = "gi" + bibits
        tebibits = "te" + bibits
        pebibits = "pe" + bibits
        exbibits = "ex" + bibits
        zebibits = "ze" + bibits
        yobibits = "yo" + bibits
    
        bytes = 'bytes'
        bibytes = 'bi' + bytes
        kibibytes = "ki" + bibytes
        mebibytes = "me" + bibytes
        gibibytes = 'gi' + bibytes
        tebibytes = 'te' + bibytes
        pebibytes = 'pe' + bibytes
        exbibytes = "ex" + bibytes
        zebibytes = "ze" + bibytes
        yobibytes = "yo" + bibytes
    
        # iperf base 2
        iperf_bytes = UnitNames.bytes
        iperf_kibibytes = UnitNames.kbytes
        iperf_mebibytes = UnitNames.mbytes
        iperf_gibibytes = UnitNames.gbytes
        iperf_tebibytes = UnitNames.tbytes
        iperf_pebibytes = UnitNames.pbytes
        iperf_exbibytes = UnitNames.ebytes
        iperf_zebibytes = UnitNames.zbytes
        iperf_yobibytes = UnitNames.ybytes
    # end BinaryUnitNames
    

::

    IDENTITY = 1
    ONE = 1.0
    BYTE = 8
    TO_BYTE = ONE/BYTE
    



Base Converter
--------------

The `BaseConverter` is a dictionary that holds conversions. It defaults to base-10 units. It takes two arguments, `to_units` a list of units that will be used as the keys for the inner dictionaries that return the conversion factors. It has to be a list that has bit-units in the first half and byte-units in the second half. The other argument (`kilo_prefix`) is used to make the conversions. For memory-related data it should be :math:`2^{10}` and for network-related data it should be :math:`10^{3}`. Because the conversions are calculated as powers of the `kilo_prefix`, the `to_units` list has to have the correct order (e.g, bits, kbits, mbits, etc.). If you were to put them in the wrong order or skip a unit then the keys would no longer match the conversion factor (for at least some of the units).

Inheritors should call 'build_conversions' in their constructor for backward compatibility with the original UnitConverter which did built th dictionary in the constructor. This call was pulled out of the `BaseConverter` so that the arguments could be set by the inheritors before calling `build_conversions`. It's kind of ugly but I didn't plan on needing more than one converter.

.. module:: iperflexer.unitconverter
.. autosummary::
   :toctree: api

   BaseConverter
   BaseConverter.prefix_conversions
   BaseConverter.bits_to_bytes
   BaseConverter.bytes_to_bits
   BaseConverter.conversions
   BaseConverter.build_conversions   
   

::

    class BaseConverter(dict):
        """
        A creator of unit-conversion dictionaries
        """
        def __init__(self, to_units, kilo_prefix):
            """
            base_converter constructor
    
            :param:
    
             - `to_units`: a list of the units to covert  to  (has to be half to-bits, half to-bytes)
             - `kilo_prefix`: kilo multiplier matching type of units
            """
            self.to_units = to_units
            self.kilo_prefix = kilo_prefix
    
            self._prefix_conversions = None
            self._bits_to_bytes = None
            self._bytes_to_bits = None
    
            # split the to_units list for later
            self.bit_conversions = self.byte_conversions = len(to_units)//2
            self.bit_units = to_units[:self.bit_conversions]
            self.byte_units = to_units[self.byte_conversions:]
            return
    
        @property
        def prefix_conversions(self):
            """
            List of lists of prefix conversions
            """
            if self._prefix_conversions is None:
                # start with list that assumes value has no prefix
                # this list is for 'bits' or 'bytes'
                # the values will be 1, 1/kilo, 1/mega, etc.
                start_list = [self.kilo_prefix**(-power)
                                             for power in xrange(self.bit_conversions)]
                self._prefix_conversions = self.conversions(conversion_factor=1,
                                                            start_list=start_list)
            return self._prefix_conversions
    
        @property
        def bits_to_bytes(self):
            """
            List of conversions for bits to bytes
            """
            if self._bits_to_bytes is None:
                self._bits_to_bytes = self.conversions(conversion_factor=TO_BYTE)
            return self._bits_to_bytes
    
        @property
        def bytes_to_bits(self):
            """
            list of conversions for bytes to bits
            """
            if self._bytes_to_bits is None:
                self._bytes_to_bits = self.conversions(conversion_factor=BYTE)
            return self._bytes_to_bits
    
        def conversions(self, conversion_factor, start_list=None):
            """
            Creates the converter-lists
    
            :param:
    
             - `conversion_factor`: multiplier for values (8 or 1/8, or 1)
             - `start_list`: if given, use to start the conversion-list
    
            :return: list of conversion_lists
            """
            if start_list is None:
                # assume that prefix_conversions exists (not safe, but...)
                start_list = self.prefix_conversions[0]
            # start with byte_factor times the base conversions (1, 1/kilo, etc.)
            converter_list = [[conversion_factor * conversion
                               for conversion in start_list]]
            for previous in xrange(self.bit_conversions - 1):
                # 'pop' last item from previous list
                # and prepend one higher-power conversion
                next_conversions = ([self.kilo_prefix**(previous+1) * conversion_factor] +
                                    converter_list[previous][:-1])
                converter_list.append(next_conversions)
            return converter_list
    
        def build_conversions(self):
            """
            builds the dictionary
            """
            # from bits to bits or bytes
            for index, units in enumerate(self.bit_units):
                self[units] = dict(zip(self.to_units, self.prefix_conversions[index] +
                                       self.bits_to_bytes[index]))
    
            # from bytes to bits or bytes        
            for index, units in enumerate(self.byte_units):
                self[units] = dict(zip(self.to_units, self.bytes_to_bits[index] +
                                       self.prefix_conversions[index]))
            return
    # end class BaseConverter
    



The UnitConverter
-----------------

The `UnitConverter` is an instance of the BaseConverter that uses the base-10 system.

.. uml::

   BaseConverter <|-- UnitConverter

.. autosummary::
   :toctree: api

   UnitConverter


Decimal To-Units List
~~~~~~~~~~~~~~~~~~~~~
   
The `decimal_to_units` list defines the valid conversions for the `UnitConverter`

::

    bit_units = [UnitNames.bits,
                 UnitNames.kbits,
                 UnitNames.mbits,
                 UnitNames.gbits,
                 UnitNames.terabits,
                 UnitNames.petabits,
                 UnitNames.exabits,
                 UnitNames.zettabits,
                 UnitNames.yottabits]
    
    byte_units = [UnitNames.bytes,
                  UnitNames.kbytes,
                  UnitNames.mbytes,
                  UnitNames.gbytes,
                  UnitNames.terabytes,
                  UnitNames.petabytes,
                  UnitNames.exabytes,
                  UnitNames.zettabytes,
                  UnitNames.yottabytes]
    
    decimal_to_units = bit_units + byte_units
    
        
    



As noted above, the `UnitConverter` is a base-10 converter so it uses the `KILO` variable as its base.

::

    KILO = 10**3
    




.. note:: The meaning of the prefixes is different for the Transfer and the Bandwidth columns. The Transfer refers to binary data so it is in base-2 (e.g. `kilo` means :math:`2^{10}`) while Bandwidth is a network-value so it is in base-10 (`kilo` means :math:`10^3`). So this converter only works for Bandwidth.

DecimalUnitConverter
~~~~~~~~~~~~~~~~~~~~

Since the `UnitConverter` was created before I thought I needed a `BinaryUnitConverter` it was just called the `UnitConverter`. To keep from breaking the code that uses it I'll leave the name the same, but add an alias called the `DecimalUnitConverter` to make a less ambiguous name.

.. '

::

    DecimalUnitConverter = UnitConverter
    




The BinaryUnitConverter
-----------------------

The `BinaryUnitConverter` is meant for the Binary (base-2) prefixed values found in the `Transfer` column. The wikipedia page on `kibibytes <https://en.wikipedia.org/wiki/Kibibyte>`_ has information about what this is about. In a nutshell it's needed because the convention for memory is to interpret the prefixes (kilo, mega, etc.) as a power of 2 rather than a power of 10 the way networking conventions interpret them.

.. '

Binary To Units
~~~~~~~~~~~~~~~

The 'binary_to_units' define what the valid conversions are.

::

    to_bits = [BinaryUnitNames.bits,
               BinaryUnitNames.kibibits,
               BinaryUnitNames.mebibits,
               BinaryUnitNames.gibibits,
               BinaryUnitNames.tebibits,
               BinaryUnitNames.pebibits,
               BinaryUnitNames.exbibits,
               BinaryUnitNames.zebibits,
               BinaryUnitNames.yobibits]
    
    to_bytes = [BinaryUnitNames.bytes,
                BinaryUnitNames.kibibytes,
                BinaryUnitNames.mebibytes,
                BinaryUnitNames.gibibytes,
                BinaryUnitNames.tebibytes,
                BinaryUnitNames.pebibytes,
                BinaryUnitNames.exbibytes,
                BinaryUnitNames.zebibytes,
                BinaryUnitNames.yobibytes]
    
    binary_to_units = to_bits + to_bytes
    



The Base Prefix Converter
~~~~~~~~~~~~~~~~~~~~~~~~~

As noted above, this is a base-2 converter so all the unit converters are powers of 2. They use :math:`2^{10}` as their base.

::

    KIBI = 2**10
    



The BinaryUnitconverter Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. uml::

   BaseConverter <|-- BinaryUnitconverter

.. autosummary::
   :toctree: api

   BinaryUnitconverter

The `BinaryUnitconverter` initializes its parent and then calls its `build_conversions` method.



The IperfbinaryConverter
------------------------

After creating the binary converter I realized that iperf doesn't use the bibyte naming convention. 

.. '

Iperf Binary To Units
~~~~~~~~~~~~~~~~~~~~~

The 'iperf_binary_to_units' define what the valid conversions are. Since the main idea is for this to be used to convert the Transfer column using the units given in the file I'm only changing the bytes-based names since Iperf always reports the output in bytes and I hope this will keep it less ambiguous. If conversions are being used outside of this case it's probably better to use the BinaryUnitConverter anyway.

.. note:: Iperf's `stdio.h` file seems to indicate that only units up to Gbits and GBytes are supported so I'm only guessing as to what the output might be if they change it.

::

    to_bits = [BinaryUnitNames.bits,
               BinaryUnitNames.kibibits,
               BinaryUnitNames.mebibits,
               BinaryUnitNames.gibibits,
               BinaryUnitNames.tebibits,
               BinaryUnitNames.pebibits,
               BinaryUnitNames.exbibits,
               BinaryUnitNames.zebibits,
               BinaryUnitNames.yobibits]
    
    to_bytes = [BinaryUnitNames.iperf_bytes,
                BinaryUnitNames.iperf_kibibytes,
                BinaryUnitNames.iperf_mebibytes,
                BinaryUnitNames.iperf_gibibytes,
                BinaryUnitNames.iperf_tebibytes,
                BinaryUnitNames.iperf_pebibytes,
                BinaryUnitNames.iperf_exbibytes,
                BinaryUnitNames.iperf_zebibytes,
                BinaryUnitNames.iperf_yobibytes]
    
    iperf_binary_to_units = to_bits + to_bytes
    



The Base 2 Prefix Converter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As noted above, this is a base-2 converter so all the unit converters are powers of 2. They use :math:`2^{10}` as their base.

The IperfbinaryConverter Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. uml::

   BaseConverter <|-- IperfbinaryConverter

.. autosummary::
   :toctree: api

   IperfbinaryConverter

The `IperfbinaryConverter` initializes its parent and then calls its `build_conversions` method.




Example Use
-----------

The expected way to use this is to multiply your original value by the value returned by the converter. For instance, to convert from bits to Mbits you could do this.

::

    if __name__ == "__builtin__":
        unit_converter = UnitConverter()
        bits = 10**6
        converted = bits * unit_converter['bits']['Mbits']
        print("{0} Mbits".format(converted))
    
    

::

    1.0 Mbits
    
    



And to convert from Mebibytes to bits you could do this.

::

    if __name__ == "__builtin__":
        binary_converter = BinaryUnitconverter()
        MBytes = 1
        bits = MBytes * binary_converter[BinaryUnitNames.mebibytes][UnitNames.bits]
        print("{0:,} bits".format(bits))
    

::

    8,388,608 bits
    



That previous example was half-way to the original use-case for creating the `BinaryUnitConverter` -- converting the data-transferred to bits so that I could calculate the transferred Megabits.

::

    if __name__ == '__builtin__':
        mbits = bits * unit_converter[UnitNames.bits][UnitNames.mbits]
        print('{0} Mbits'.format(mbits))
    

::

    8.388608 Mbits
    

