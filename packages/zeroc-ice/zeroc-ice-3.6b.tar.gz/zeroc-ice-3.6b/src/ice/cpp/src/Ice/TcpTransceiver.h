// **********************************************************************
//
// Copyright (c) 2003-2014 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#ifndef ICE_TCP_TRANSCEIVER_H
#define ICE_TCP_TRANSCEIVER_H

#include <Ice/ProtocolInstanceF.h>
#include <Ice/Transceiver.h>
#include <Ice/Network.h>
#include <Ice/StreamSocket.h>

namespace IceInternal
{

class TcpConnector;
class TcpAcceptor;

class TcpTransceiver : public Transceiver
{
public:

    virtual NativeInfoPtr getNativeInfo();

    virtual SocketOperation initialize(Buffer&, Buffer&, bool&);
    virtual SocketOperation closing(bool, const Ice::LocalException&);
    virtual void close();
    virtual SocketOperation write(Buffer&);
    virtual SocketOperation read(Buffer&, bool&);
#ifdef ICE_USE_IOCP
    virtual bool startWrite(Buffer&);
    virtual void finishWrite(Buffer&);
    virtual void startRead(Buffer&);
    virtual void finishRead(Buffer&, bool&);
#endif
    virtual std::string protocol() const;
    virtual std::string toString() const;
    virtual std::string toDetailedString() const;
    virtual Ice::ConnectionInfoPtr getInfo() const;
    virtual void checkSendSize(const Buffer&);

private:

    TcpTransceiver(const ProtocolInstancePtr&, const StreamSocketPtr&);
    virtual ~TcpTransceiver();

    friend class TcpConnector;
    friend class TcpAcceptor;

    const ProtocolInstancePtr _instance;
    const StreamSocketPtr _stream;
};

}

#endif
