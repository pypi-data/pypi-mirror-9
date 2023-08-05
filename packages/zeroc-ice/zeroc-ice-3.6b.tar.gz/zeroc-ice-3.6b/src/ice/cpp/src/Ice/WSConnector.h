// **********************************************************************
//
// Copyright (c) 2003-2014 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#ifndef ICE_WSCONNECTOR_I_H
#define ICE_WSCONNECTOR_I_H

#include <Ice/LoggerF.h>
#include <Ice/TransceiverF.h>
#include <Ice/Connector.h>
#include <Ice/ProtocolInstance.h>

namespace IceInternal
{

class WSEndpoint;

class WSConnector : public Connector
{
public:

    virtual TransceiverPtr connect();

    virtual Ice::Short type() const;
    virtual std::string toString() const;

    virtual bool operator==(const Connector&) const;
    virtual bool operator!=(const Connector&) const;
    virtual bool operator<(const Connector&) const;

private:

    WSConnector(const ProtocolInstancePtr&, const ConnectorPtr&, const std::string&, int, const std::string&);
    virtual ~WSConnector();
    friend class WSEndpoint;

    const ProtocolInstancePtr _instance;
    const ConnectorPtr _delegate;
    const std::string _host;
    const int _port;
    const std::string _resource;
};

}

#endif
