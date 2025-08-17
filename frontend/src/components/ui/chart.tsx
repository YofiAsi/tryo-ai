"use client"

// Temporarily disabled due to TypeScript issues with Recharts
// This component will be re-enabled once the type issues are resolved

/*
import * as React from "react"
import * as RechartsPrimitive from "recharts"

import { cn } from "@/lib/utils"

// Format: { THEME_NAME: CSS_SELECTOR }
const THEMES = { light: "", dark: ".dark" } as const

export type ChartConfig = {
  [k in string]: {
    label?: React.ReactNode
    icon?: React.ComponentType
  } & (
    | { color?: string; theme?: never }
    | { color?: never; theme: Record<keyof typeof THEMES, string> }
  )
}

type ChartContextProps = {
  config: ChartConfig
}

const ChartContext = React.createContext<ChartContextProps | null>(null)

function useChart() {
  const context = React.useContext(ChartContext)

  if (!context) {
    throw new Error("useChart must be used within a <ChartContainer />")
  }

  return context
}

const ChartContainer = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<"div"> & {
    config: ChartConfig
    children: React.ComponentProps<
      typeof RechartsPrimitive.ResponsiveContainer
    >["children"]
  }
>(({ id, className, children, config, ...props }, ref) => {
  const uniqueId = React.useId()
  const chartId = `chart-${id || uniqueId.replace(/:/g, "")}`

  return (
    <ChartContext.Provider value={{ config }}>
      <div
        data-chart={chartId}
        ref={ref}
        className={cn(
          "flex aspect-video justify-center text-xs [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground [&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/50 [&_.recharts-curve.recharts-tooltip-cursor]:stroke-border [&_.recharts-dot[stroke='#fff']]:stroke-transparent [&_.recharts-layer]:outline-none [&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border [&_.recharts-radial-bar-background-sector]:fill-muted [&_.recharts-rectangle.recharts-tooltip-cursor]:fill-muted [&_.recharts-reference-line_[stroke='#ccc']]:stroke-border [&_.recharts-sector[stroke='#fff']]:stroke-transparent [&_.recharts-sector]:outline-none [&_.recharts-surface]:outline-none",
          className
        )}
        {...props}
      >
        <ChartStyle id={chartId} config={config} />
        <RechartsPrimitive.ResponsiveContainer>
          {children}
        </RechartsPrimitive.ResponsiveContainer>
      </div>
    </ChartContext.Provider>
  )
})
ChartContainer.displayName = "Chart"

const ChartStyle = ({ id, config }: { id: string; config: ChartConfig }) => {
  const colorConfig = Object.entries(config).filter(
    ([_, config]) => config.theme || config.color
  )

  if (!colorConfig.length) {
    return null
  }

  return (
    <style
      dangerouslySetInnerHTML={{
        __html: Object.entries(THEMES)
          .map(
            ([theme, prefix]) => `
${prefix} [data-chart=${id}] {
${colorConfig
  .map(([key, itemConfig]) => {
    const color =
      itemConfig.theme?.[theme as keyof typeof itemConfig.theme] ||
      itemConfig.color
    return color ? `  --color-${key}: ${color};` : null
  })
  .join("\n")}
}
`
          )
          .join("\n"),
      }}
    />
  )
}

ChartStyle.displayName = "ChartStyle"

const ChartTooltip = RechartsPrimitive.Tooltip

const ChartTooltipContent = React.forwardRef<
  React.ElementRef<typeof RechartsPrimitive.Tooltip>,
  React.ComponentProps<typeof RechartsPrimitive.Tooltip> &
    React.ComponentProps<"div"> & {
      payload?: any[]
      label?: string
      active?: boolean
      config?: ChartConfig
    }
>(({ payload, label, active, config, className, children, ...props }, ref) => {
  const { config: chartConfig } = useChart()

  if (!active || !payload) {
    return null
  }

  const { label: labelStyle, ...labelStyles } = chartConfig[payload[0]?.dataKey] || {}

  return (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border bg-background p-2 text-sm shadow-sm",
        className
      )}
      style={{
        ...labelStyles,
        ...(labelStyle && {
          "--tw-rotate": `var(--rotation, ${labelStyle}deg)`,
        } as React.CSSProperties),
      }}
      {...props}
    >
      <div className="grid grid-cols-2 gap-2">
        {payload.map((item, index) => {
          const { label: itemLabel = item.dataKey, ...itemStyles } =
            chartConfig[item.dataKey] || {}

          return (
            <div
              key={index}
              className="flex items-center gap-2"
              style={itemStyles}
            >
              <div
                className="flex h-2 w-2 rounded-full"
                style={{
                  backgroundColor:
                    item.color ||
                    (itemStyles as any)?.color ||
                    "hsl(var(--chart-1))",
                }}
              />
              <span className="text-muted-foreground">{itemLabel}:</span>
              <span className="font-medium tabular-nums">
                {item.value instanceof Date
                  ? item.value.toLocaleDateString()
                  : item.value}
              </span>
            </div>
          )
        })}
      </div>
      {children}
    </div>
  )
})

ChartTooltipContent.displayName = "ChartTooltipContent"

const ChartLegend = RechartsPrimitive.Legend

const ChartLegendContent = React.forwardRef<
  React.ElementRef<typeof RechartsPrimitive.Legend>,
  React.ComponentProps<typeof RechartsPrimitive.Legend> &
    Pick<RechartsPrimitive.LegendProps, "payload" | "verticalAlign"> & {
      config?: ChartConfig
    }
>(({ config, payload, ...props }, ref) => {
  const { config: chartConfig } = useChart()

  if (!payload?.length) {
    return null
  }

  return (
    <div
      ref={ref}
      className="flex items-center gap-4 text-xs"
      {...props}
    >
      {payload.map((item) => {
        const { label = item.value, ...itemStyles } =
          chartConfig[item.dataKey] || {}

        return (
          <div
            key={item.dataKey}
            className="flex items-center gap-1.5"
            style={itemStyles}
          >
            <div
              className="flex h-2 w-2 rounded-full"
              style={{
                backgroundColor:
                  item.color ||
                  (itemStyles as any)?.color ||
                  "hsl(var(--chart-1))",
              }}
            />
            <span className="text-muted-foreground">{label}</span>
          </div>
        )
      })}
    </div>
  )
})

ChartLegendContent.displayName = "ChartLegendContent"

export {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  ChartStyle,
}
*/

// Temporary placeholder exports
export const ChartContainer = () => null
export const ChartTooltip = () => null
export const ChartTooltipContent = () => null
export const ChartLegend = () => null
export const ChartLegendContent = () => null
export const ChartStyle = () => null
