/*
 * This file was codegened from codegen.h.mako.
 */
#include "${name.lower()}.hpp"

using namespace std;

ostream& ${name}::serialize(ostream& output) const
{
<% c = '' %>\
% for field, ctype in dtype:
  output << "${c}" << ${field};
<% c = ' ' %>\
% endfor
  output << endl;
  return output;
}

istream& ${name}::deserialize(istream& input)
{
    // Use a reasonably long buffer -- longer than we expect any line to
    // be.
    char input_buffer[8096] = {0};

    // Read from the file until we see a valid line.
    while (!input.eof() && (strlen(input_buffer) == 0 ||
           input_buffer[0] == '\n' || input_buffer[0] == '#'))
    {
        input.getline(input_buffer, 8096);
    }

    basic_array_source<char> input_source(input_buffer, strlen(input_buffer));
    stream<basic_array_source<char> > input_stream(input_source);

% for field, ctype in dtype:
    input_stream >> ${field};
% endfor

    return input;
}

const string& ${name}::get_header_string() const
{
    static const string header("${schema.to_string().replace('\n', '\\n')}");
    return header;
}

/*
 * A function to make sure we have a reasonable file header. For simplicity
 * we only check that the first line makes sense. The remaining lines
 * may or may not make sense, but we'll find out if the types are wrong
 * when we try to parse the data anyway, and there's nothing we can do about
 * the indexing at runtime.
 *
 * A better approach might be to invoke the python parser to verify that it
 * matches expectations. For now, this isn't done so as to avoid PYTHONPATH
 * issues, and so the C++ implementation can stand on its own without requiring
 * python.
 */
bool
${name}::is_valid_header(istream& input)
{
    // Note that when we detect a problem, we continue to parse
    // the rest of the header so that the file pointer will be
    // where the called expects.
    char readbuffer[4096] = {};
    bool retval = true;

    // Check the first line;
    input >> readbuffer;
    if (strncmp(readbuffer, "#@esv", 4) != 0) {
#ifdef DEBUG
        cerr << "'" << readbuffer << "' vs '" << "#@esv" << "'\n"; // debug
        cerr.flush();
#endif
        retval = false;
    }

% for field, ftype in dtype:
    input >> readbuffer;
    if (strncmp(readbuffer, "${field}", strlen("${field}")) != 0) {
#ifdef DEBUG
        cerr << "'" << readbuffer << "' vs '" << "${field}" << "'\n"; // debug
        cerr.flush();
#endif
        retval = false;
    }
% endfor

    return retval;
}


// Singleton implementation
${name}Collection singleton_${name}Collection;

${name}CollectionRef get_${name}Collection()
{
    return singleton_${name}Collection;
}
