import { useEffect } from "react";

import { fetch, useBoolean } from "@/utils";
import { LocalCogneeIcon } from "@/ui/Icons";

import DatasetsAccordion, { DatasetsAccordionProps } from "./DatasetsAccordion";

type InstanceDatasetsAccordionProps = Omit<DatasetsAccordionProps, "title">;

export default function InstanceDatasetsAccordion({ onDatasetsChange }: InstanceDatasetsAccordionProps) {
  const {
    value: isLocalCogneeConnected,
    setTrue: setLocalCogneeConnected,
  } = useBoolean(false);

  useEffect(() => {
    const checkConnectionToLocalCognee = () => {
      fetch.checkHealth()
        .then(setLocalCogneeConnected)
        .catch(() => {});
    };

    checkConnectionToLocalCognee();
    // CozyCognee Patch: 完全删除 cloud cognee 相关功能
    // 只保留 local cognee 功能
  }, [setLocalCogneeConnected]);

  return (
    <div className="flex flex-col">
      <DatasetsAccordion
        title={(
          <div className="flex flex-row items-center justify-between">
            <div className="flex flex-row items-center gap-2">
              <LocalCogneeIcon className="text-indigo-700" />
              <span className="text-xs">local cognee</span>
            </div>
          </div>
        )}
        tools={isLocalCogneeConnected ? <span className="text-xs text-indigo-600">Connected</span> : <span className="text-xs text-gray-400">Not connected</span>}
        switchCaretPosition={true}
        className="pt-3 pb-1.5"
        contentClassName="pl-4"
        onDatasetsChange={onDatasetsChange}
      />

      {/* CozyCognee Patch: 删除所有 cloud cognee 相关内容 */}
    </div>
  );
}
