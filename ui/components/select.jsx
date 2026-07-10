import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from "@headlessui/react"
import { CaretDownIcon } from "@phosphor-icons/react"

import { cn } from "@/utils/cn"

export function Select({ options, value, onChange, className }) {
  const selectedOption = options.find((opt) => opt.value === value)

  return (
    <Listbox value={value} onChange={onChange}>
      <ListboxButton
        className={cn(
          "group flex-center gap-2 w-full h-8 px-3 rounded-sm cursor-pointer transition",
          "bg-background hover:bg-background-dark/50 border border-b-muted active:border-muted",
          "data-open:bg-background-dark/50 data-open:border-muted",
          className,
        )}
      >
        <span className="flex-1 text-left truncate">{selectedOption?.label}</span>
        <CaretDownIcon className="size-4 text-secondary shrink-0 transition-all group-data-open:rotate-180" />
      </ListboxButton>

      <ListboxOptions
        anchor="bottom"
        className="w-(--button-width) mt-1 p-1 space-y-1 border bg-background/80 backdrop-blur-sm shadow-lg/10 rounded-md transition data-closed:-translate-y-2 data-closed:opacity-0"
        transition
      >
        {options.map((item) => (
          <ListboxOption
            key={item.value}
            value={item.value}
            className={cn(
              "group relative flex items-center gap-1 h-8 px-3 rounded-sm cursor-pointer transition",
              "hover:bg-background-dark data-selected:bg-background-dark",
            )}
          >
            {item.label}
            <div className="absolute left-0 w-0.75 h-3.5 rounded-full bg-accent group-data-selected:block hidden" />
          </ListboxOption>
        ))}
      </ListboxOptions>
    </Listbox>
  )
}
