import { TextboxIcon } from "@phosphor-icons/react"

import { Page, PageBlock } from "@/components/page.jsx"

export function Renamer() {
  return (
    <Page>
      <PageBlock className="flex-1 flex-center flex-col gap-3" last>
        <TextboxIcon size={44} weight="light" className="text-accent" />
        <div className="text-center">
          <p className="text-base font-medium">Bangumi Renamer</p>
          <p className="mt-1 text-secondary">动画重命名功能将在这里构建</p>
        </div>
      </PageBlock>
    </Page>
  )
}
