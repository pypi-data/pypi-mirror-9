// **********************************************************************
//
// Copyright (c) 2003-2014 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#include <IceUtil/Time.h>
#include <Ice/LoggerI.h>
#include <IceUtil/Mutex.h>
#include <IceUtil/MutexPtrLock.h>

#ifdef _WIN32
#  include <IceUtil/StringUtil.h>
#  include <IceUtil/ScopedArray.h>
#endif

#include <Ice/LocalException.h>

using namespace std;
using namespace Ice;
using namespace IceInternal;

namespace
{

IceUtil::Mutex* outputMutex = 0;

class Init
{
public:

    Init()
    {
        outputMutex = new IceUtil::Mutex;
    }

    ~Init()
    {
        delete outputMutex;
        outputMutex = 0;
    }
};

Init init;

}

Ice::LoggerI::LoggerI(const string& prefix, const string& file, 
                      bool convert, const IceUtil::StringConverterPtr& converter) :
    _prefix(prefix),
    _convert(convert),
    _converter(converter)
#if defined(_WIN32) && !defined(ICE_OS_WINRT)
    , _consoleConverter(new IceUtil::WindowsStringConverter(GetConsoleOutputCP()))
#endif

{
    if(!prefix.empty())
    {
        _formattedPrefix = prefix + ": ";
    }

    if(!file.empty())
    {
        _file = file;
        _out.open(file, fstream::out | fstream::app);
        if(!_out.is_open())
        {
            throw InitializationException(__FILE__, __LINE__, "FileLogger: cannot open " + _file);
        }
    }
}

Ice::LoggerI::~LoggerI()
{
    if(_out.is_open())
    {
        _out.close();
    }
}

void
Ice::LoggerI::print(const string& message)
{
    write(message, false);
}

void
Ice::LoggerI::trace(const string& category, const string& message)
{
    string s = "-- " + IceUtil::Time::now().toDateTime() + " " + _formattedPrefix;
    if(!category.empty())
    {
        s += category + ": ";
    }
    s += message;

    write(s, true);
}

void
Ice::LoggerI::warning(const string& message)
{
    write("-! " + IceUtil::Time::now().toDateTime() + " " + _formattedPrefix + "warning: " + message, true);
}

void
Ice::LoggerI::error(const string& message)
{
    write("!! " + IceUtil::Time::now().toDateTime() + " " + _formattedPrefix + "error: " + message, true);
}

string
Ice::LoggerI::getPrefix()
{
    return _prefix;
}

LoggerPtr
Ice::LoggerI::cloneWithPrefix(const std::string& prefix)
{
    return new LoggerI(prefix, _file, _convert, _converter);
}

void
Ice::LoggerI::write(const string& message, bool indent)
{
    IceUtilInternal::MutexPtrLock<IceUtil::Mutex> sync(outputMutex);

    string s = message;

    if(indent)
    {
        string::size_type idx = 0;
        while((idx = s.find("\n", idx)) != string::npos)
        {
            s.insert(idx + 1, "   ");
            ++idx;
        }
    }

    if(_out.is_open())
    {
        _out << s << endl;
    }
    else
    {
#if !defined(_WIN32) || defined(ICE_OS_WINRT)
        cerr << s << endl;
#else
        //
        // Convert the message from the native narrow string encoding to the console
        // code page encoding for printing. If the _convert member is set to false 
        // we don't do any conversion.
        //
        if(!_convert)
        {
            //
            // Use fprintf_s to avoid encoding conversion when stderr is connected
            // to Windows console. When _convert is set to false we always output
            // UTF-8 encoded messages.
            //
            fprintf_s(stderr, "%s\n", IceUtil::nativeToUTF8(s, _converter).c_str());
            fflush(stderr);
        }
        else
        {
            try
            {
                // Convert message to UTF-8
                string u8s = IceUtil::nativeToUTF8(s, _converter);
                
                // Then from UTF-8 to console CP
                string consoleString;
                _consoleConverter->fromUTF8(reinterpret_cast<const Byte*>(u8s.data()),
                                            reinterpret_cast<const Byte*>(u8s.data() + u8s.size()), 
                                            consoleString);

                // We cannot use cerr here as writing to console using cerr
                // will do its own conversion and will corrupt the messages.
                //
                fprintf_s(stderr, "%s\n", consoleString.c_str());
            }
            catch(const IceUtil::IllegalConversionException&)
            {
                //
                // If there is a problem with the encoding conversions we just
                // write the original message without encoding conversions.
                //
                fprintf_s(stderr, "%s\n", s.c_str());
            }
            fflush(stderr);
        }
#endif
    }
}
