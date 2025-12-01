"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect } from "react";
import { useBoolean, fetch } from "@/utils";

import { CogneeIcon } from "../Icons";
import { StatusDot } from "../elements";

interface HeaderProps {
  user?: {
    name: string;
    email: string;
    picture: string;
  };
}

export default function Header({ user }: HeaderProps) {
  const {
    value: isMCPConnected,
    setTrue: setMCPConnected,
    setFalse: setMCPDisconnected,
  } = useBoolean(false);

  useEffect(() => {
    const checkMCPConnection = () => {
      fetch.checkMCPHealth()
        .then(() => setMCPConnected())
        .catch(() => setMCPDisconnected());
    };

    checkMCPConnection();
    const interval = setInterval(checkMCPConnection, 30000);
    
    return () => clearInterval(interval);
  }, [setMCPConnected, setMCPDisconnected]);

  return (
    <>
      <header className="relative flex flex-row h-14 min-h-14 px-5 items-center justify-between w-full max-w-[1920px] mx-auto">
        <div className="flex flex-row gap-4 items-center">
          <CogneeIcon />
          <div className="text-lg">Cognee Local</div>
        </div>

        <div className="flex flex-row items-center gap-2.5">
          <Link href="/mcp-status" className="!text-indigo-600 pl-4 pr-4">
            <StatusDot className="mr-2" isActive={isMCPConnected} />
            { isMCPConnected ? "MCP connected" : "MCP disconnected" }
          </Link>
          {/* CozyCognee Patch: 删除 Sync 按钮、Premium 链接和 API keys 链接 */}
          {/* <div className="px-2 py-2 mr-3">
            <SettingsIcon />
          </div> */}
          <Link href="/account" className="bg-indigo-600 w-8 h-8 rounded-full overflow-hidden">
            {user?.picture ? (
              <Image width="32" height="32" alt="Name of the user" src={user.picture} />
            ) : (
              <div className="w-8 h-8 rounded-full text-white flex items-center justify-center">
                {user?.email?.charAt(0) || "C"}
              </div>
            )}
          </Link>
        </div>
      </header>
    </>
  );
}

