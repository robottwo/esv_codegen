/*
 * This file was codegened from codegen.hpp.mako.
 *
 */

#ifndef ${name}_H_
#define ${name}_H_

#include <boost/iostreams/device/array.hpp>
#include <boost/iostreams/stream.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/multi_index/hashed_index.hpp>
#include <boost/multi_index/identity.hpp>
#include <boost/multi_index/member.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/typeof/typeof.hpp>

#include <exception>
#include <fstream>
#include <iostream>
#include <string>

using namespace ::boost;
using namespace ::boost::iostreams;
using namespace ::boost::multi_index;
using namespace ::std;

const char END_OF_${name}[] = "#END_OF_${name}";

/**
 * This implements a basic data container for ${name}.  For anything
 * other than a trivial data container, this class should be
 * inherited and extended.
 *
 * The basic principal is that everything needed for persistence is
 * described in ${name}, and any runtime functionality is defined
 * in the derived class.
 */
struct ${name} {
% for key, ctype in dtype:
    ${ctype} ${key};
% endfor

    /*
     * Member constructor
     */
    ${name}(\
<% c = '' %>\
% for key, ctype in dtype:
${c}const ${ctype} & in_${key} \
<% c = '        ,' %>
% endfor
    ) : \
<% c = '' %>\
% for key, ctype in dtype:
${c}${key}(in_${key})\
<% c = '        ,' %>
% endfor
        {}

    /**
     * Copy constructor
     */
    ${name}(const ${name} & other)
        : \
<% c = '' %>\
% for key, ctype in dtype:
${c}${key}(other.${key})\
<% c = '        ,' %>
% endfor
        {}

    /**
     * Default constructor.
     */
    ${name}() :
<% c = '    ' %>\
% for key, ctype in dtype:
% if ctype == 'std::string':
   ${c}${key}("_")
% elif ctype in ['short', 'int', 'long', 'float', 'double']:
    ${c}${key}((${ctype})0)
% endif
<% c = '   ,' %>\
% endfor
    {}

    /**
     * Ascii serializer. Writes the current object as a single line.
     */
    virtual ostream& serialize(ostream& output) const;

    /**
     * Ascii Deserializer -- loads one line from input, and populates
     * the current data. Will skip comment and blank lines
     * automatically. Will raise an exception if the line does not
     * conform to the expected data format.
     */
    virtual istream& deserialize(istream& input);

    /**
     * Return a multiline ascii file header.
     */
    virtual const string & get_header_string() const;

    /**
     * Validate that the header in the istream represents this object
     * type. May forward the istream to the end of the header.
     */
    static bool is_valid_header(istream& input);


%if len(keys) > 0:
    /**
     * The greater than and less than operators are shallow, and only compare object indices.
     */
    bool operator<(const ${name} & other) const
    {
        return ${keys[0]} < other.${keys[0]};
    }

    /**
     * The greater than and less than operators are shallow, and only compare object indices.
     */
    bool operator>(const ${name} & other) const
    {
        return ${keys[0]} > other.${keys[0]};
    }

%endif

    /**
     * The equals and not equals operators are deep, and compare all the object's properties.
     */
    bool operator==(const ${name} & other) const
    {
       return (
<% c = '' %>\
% for field, ctype in dtype:
%if ctype == 'std::string':
               ${c} (${field}.compare(other.${field}) == 0)
%else:
               ${c} (${field} == other.${field})
%endif
<% c = '&&' %>\
% endfor
        );
    }

    bool operator!=(const ${name} & other) const
    {
        return ! (*this == other);
    }
};

// Lookup Tags
struct ${name}_by_id {};
% for key, ctype in dtype:
% if key in keys:
struct ${name}_by_${key} {};
% endif
% if key in indices:
struct ${name}s_by_${key} {};
% endif
% endfor

/**
 * This class represents an error while parsing.
 */
class ${name}ParsingException : public std::exception
{
  public:
    ${name}ParsingException(const char * in_message) throw()
    {
        strncpy(message, in_message, 4096);
    }
    virtual const char* what() const throw()
    {
        return message;
    }
  private:
    char message[4096];
};

/**
* This class represents an error while looking up a key field.
*/
class ${name}NotFoundException : public std::exception
{
  public:
    ${name}NotFoundException(const char * in_message) throw()
    {
        strncpy(message, in_message, 4096);
    }
    ${name}NotFoundException(const std::string & in_message) throw()
    {
        strncpy(message, in_message.c_str(), 4096);
    }
    virtual const char* what() const throw()
    {
        return message;
    }
  private:
    char message[4096];
};

/**
 * The following struct is used to modify ${name}s in-place. Only non-key types are updated.
 */
struct ${name}_modify_struct
{
    ${name}_modify_struct(const ${name} & new_vals) : new_vals(new_vals) {}

    void operator()(${name}& entry) {
% for key, ctype in dtype:
% if key not in keys:
        entry.${key} = new_vals.${key};
% else:
        if (entry.${key} != new_vals.${key}) {
            throw(${name}NotFoundException(std::string("${key}")));
        }
% endif
% endfor
    }

private:
    ${name} new_vals;
};


/**
 * This template class describes a collection of ${name} objects,
 * or objects derived from ${name}.
 *
 * Note that this implementation uses boost multi_index_containers,
 * and these collections are *NOT* thread safe. It is safe to read
 * from any number of threads, but callers must ensure that writers
 * have exclusive access to these objects
 *
 * T must be derived from ${name}.
 */
template <class T>
//std::enable_if<std::is_base_of<${name},T>::value>:type
class ${name}sCollection_ : public multi_index_container<
    T,
    indexed_by<ordered_unique<tag<${name}_by_id>, identity<T> >
<% c = '        ,' %> \
% for key, ctype in dtype:
% if key in keys:
    ${c}hashed_unique<tag<${name}_by_${key}>, member<${name}, ${ctype}, &${name}::${key}> >
% endif
% if key in indices:
    ${c}hashed_non_unique<tag<${name}s_by_${key}>, member<${name}, ${ctype}, &${name}::${key}> >
% endif
% endfor
    >
>
{
  public:
% for field, ftype in dtype:
% if field in keys:
    /**
     * Retrieve the single item with the given ${field} value. If the item doesn't exist,
     * then raise a ${name}NotFoundException.
     */
    virtual T get_by_${field}(const ${ftype} & ${field}) const throw (${name}NotFoundException)
    {
        auto found = this->get<${name}_by_${field}>().find(${field});
        if (found == this->get<${name}_by_${field}>().end()) {
        throw ${name}NotFoundException(std::string("${name} not found: ")

% if ftype == 'std::string':
                                           + std::string(${field}));

% else:
                                           + std::to_string(${field}));
% endif
        }
        else {
            return *found;
        }
    }
% elif field in indices:
    /**
     * Retrieve all the items with the given ${field}. Returns them in a vector.
     * Note that the vector may be empty.
     */
     std::vector<T> find_by_${field}(const ${ftype} & ${field}) const
    {
        std::vector<T> items;

        // ${field} is indexed, so we can just look up the values we want.
        auto found = this->get<${name}s_by_${field}>().find(${field});
        auto end   = this->get<${name}s_by_${field}>().end();
        copy(found, end, std::back_inserter(items));
        return items;
    }
% else:
    /**
     * Retrieve all the items with the given ${field}. Returns them in a vector.
     * Note that the vector may be empty.
     */
    std::vector<T> find_by_${field}(const ${ftype} & ${field}) const
    {
        std::vector<T> items;

        // ${field} isn't indexed, so we have to do a grep
        // for the values we want.
        for (T item: this->get<${name}_by_id>()) {
            if (item.${field} != ${field}) {
                items.push_back(item);
            }
        }
        return items;
    }
% endif
% endfor


    /**
     * Load the contents of the given esv file into this collection.
     */
    istream& deserialize(istream& input) {
        if (!T::is_valid_header(input)) {
            throw ${name}ParsingException("Invalid header while parsing ${name} file");
        }
        T empty_row;
        char buffer[4096] = {0};
        while (! input.eof()) {
            if (input.peek() == '#') {
                // If the next line is a comment line:
                input.getline(buffer, 4096);
                if (std::string(buffer).compare(END_OF_${name}) == 0) {
                    return input;
                }
            }
            else if (input.peek() == '\n') {
                // Skip empty lines quickly
                input.getline(buffer, 4);
            }
            else {
                T new_row;
                new_row.deserialize(input);
                if (new_row != empty_row) {
                    this->insert(new_row);
                }
            }
        } //-- end while

        return input;
    }//-- end deserialize

    /**
     * Serialize this collection to an esv-compatible format.
     */
    ostream& serialize(ostream& output) {
        output << T().get_header_string();

        for (const T & row: this->get<${name}_by_id>())    {
            row.serialize(output);
        }

        // We might want to read multiple collections from the same stream
        // later, so we add an END_OF_${name} line to the end of the output
        // as a demarcation.
        output << END_OF_${name} << '\n';
        return output;
    } //-- end serialize

 protected:
};

/**
 * A collection of ${name}s, along with various lookup types.
 * If you want to define your own collection based on something derived
 * from ${name}, you'll need to invoke this DECLARE macro. See the
 * example for ${name} below.
 */
#define DECLARE_${name}_COLLECTION(T) \\

typedef ${name}sCollection_<T> T##Collection; \\

typedef ${name}sCollection_<T> & T##CollectionRef; \\

typedef ${name}sCollection_<T>::index<${name}_by_id>::type T##s_by_id_t;\\

% for key, ctype in dtype:
% if key in keys:
typedef ${name}sCollection_<T>::index<${name}_by_${key}>::type T##_by_${key}_t; \\

%endif
% if key in indices:
typedef ${name}sCollection_<T>::index<${name}s_by_${key}>::type T##s_by_${key}_t;\\

%endif
%endfor


/**
 * typedef a container for ${name}s.
 */
DECLARE_${name}_COLLECTION(${name})


/**
 * Often, we'll want a singleton collection. So, we provide a way of accessing one.
 */
${name}CollectionRef get_${name}Collection();

#endif
