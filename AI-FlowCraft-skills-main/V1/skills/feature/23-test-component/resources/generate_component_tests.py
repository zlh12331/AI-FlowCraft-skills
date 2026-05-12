#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件测试辅助脚本 - 测试代码生成器
功能：根据扫描结果，自动生成组件测试代码骨架
支持：React (RTL)、Vue (VTU)、Angular (ATL)、Svelte
用法：python generate_component_tests.py <扫描结果JSON> <输出目录> [项目路径]
"""

import sys
from pathlib import Path

# 导入公共模块
from common import load_json


def generate_react_tests(components: list, output_dir: str, project_path: str = ""):
    """
    生成 React 组件测试代码（Jest + React Testing Library）

    Args:
        components: 组件列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    for comp in components:
        file_path = comp["file"]
        comp_name = comp["name"]
        props = comp.get("props", [])
        events = comp.get("events", [])
        state_hooks = comp.get("state_hooks", 0)
        effect_hooks = comp.get("effect_hooks", 0)
        cond_renders = comp.get("conditional_renders", 0)
        list_renders = comp.get("list_renders", 0)
        docstring = comp.get("docstring", "")

        # 生成测试文件路径
        if file_path.endswith(".tsx"):
            test_file = Path(output_dir) / file_path.replace(".tsx", ".test.tsx")
        elif file_path.endswith(".jsx"):
            test_file = Path(output_dir) / file_path.replace(".jsx", ".test.jsx")
        else:
            test_file = Path(output_dir) / file_path.replace(".ts", ".test.tsx").replace(".js", ".test.jsx")

        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 计算导入路径
        import_path = file_path.replace(".tsx", "").replace(".jsx", "").replace(".ts", "").replace(".js", "")
        depth = file_path.count("/") - 1
        prefix = "../" * (depth + 1) if depth >= 0 else "./"

        lines = []
        lines.append(f"// 自动生成的组件测试 - {comp_name}")
        lines.append(f"// 测试框架: Jest + React Testing Library")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据组件源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';")
        lines.append(f"import userEvent from '@testing-library/user-event';")
        lines.append(f"import {comp_name} from '{prefix}{import_path}';")
        lines.append("")

        # Mock 说明
        if effect_hooks > 0:
            lines.append(f"// 组件使用了 {effect_hooks} 个 useEffect，可能需要 Mock 以下模块：")
            lines.append(f"// - 路由: jest.mock('next/navigation', () => ({{ useRouter: () => ({{ push: jest.fn() }}) }}))")
            lines.append(f"// - API: jest.mock('@/lib/api', () => ({{ fetchData: jest.fn() }}))")
            lines.append(f"// - 状态管理: jest.mock('@/store', () => ({{ useStore: () => ({{ ... }}) }}))")
            lines.append("")

        lines.append(f"describe('{comp_name}', () => {{")
        lines.append(f"  // 组件位置: {file_path}")
        if props:
            lines.append(f"  // Props: {', '.join(props)}")
        if events:
            lines.append(f"  // Events: {', '.join(events)}")
        if state_hooks:
            lines.append(f"  // 内部状态: {state_hooks} 个 useState")
        if cond_renders:
            lines.append(f"  // 条件渲染: {cond_renders} 处")
        if list_renders:
            lines.append(f"  // 列表渲染: {list_renders} 处")
        if docstring:
            lines.append(f"  // 说明: {docstring.split(chr(10))[0].strip(' /*')}")
        lines.append("")

        # === 渲染测试 ===
        lines.append(f"  describe('渲染测试', () => {{")
        lines.append(f"    it('使用默认 Props 应正确渲染', () => {{")
        lines.append(f"      render(<{comp_name} />);")
        lines.append(f"      // TODO: 验证组件渲染了关键内容")
        lines.append(f"      // expect(screen.getByText('...')).toBeInTheDocument();")
        lines.append(f"    }});")
        lines.append("")

        if props:
            lines.append(f"    it('传入所有 Props 应正确渲染对应内容', () => {{")
            # 生成 Props 对象
            props_obj = ", ".join([f"{p}: '{p}_value'" for p in props[:5]])
            lines.append(f"      render(<{comp_name} {{{props_obj}}} />);")
            lines.append(f"      // TODO: 验证每个 Prop 对应的渲染内容")
            for p in props[:3]:
                lines.append(f"      // expect(screen.getByText('{p}_value')).toBeInTheDocument();")
            lines.append(f"    }});")
            lines.append("")

        lines.append(f"  }});")
        lines.append("")

        # === 交互测试 ===
        if events or state_hooks > 0:
            lines.append(f"  describe('交互测试', () => {{")
            if events:
                for event in events[:3]:
                    handler = event[2:].lower()  # onClick -> click
                    handler_name = f"handle{event}"
                    lines.append(f"    it('触发 {event} 应调用回调函数', async () => {{")
                    lines.append(f"      const user = userEvent.setup();")
                    lines.append(f"      const {handler_name} = jest.fn();")
                    # 使用字符串拼接避免 f-string 嵌套花括号
                    jsx_props = f"{event}:={{ {handler_name} }}"
                    lines.append(f"      render(<{comp_name} {{{jsx_props}}} />);")
                    lines.append(f"      // TODO: 找到触发 {event} 的元素并交互")
                    lines.append(f"      // await user.click(screen.getByRole('button'));")
                    lines.append(f"      expect({handler_name}).toHaveBeenCalled();")
                    lines.append(f"    }});")
                    lines.append("")
            else:
                lines.append(f"    it('用户交互应触发状态变化', async () => {{")
                lines.append(f"      const user = userEvent.setup();")
                lines.append(f"      render(<{comp_name} />);")
                lines.append(f"      // TODO: 执行用户操作（点击、输入等）")
                lines.append(f"      // await user.click(screen.getByRole('button'));")
                lines.append(f"      // TODO: 验证状态变化后的渲染结果")
                lines.append(f"    }});")
                lines.append("")
            lines.append(f"  }});")
            lines.append("")

        # === 条件渲染测试 ===
        if cond_renders > 0:
            lines.append(f"  describe('条件渲染测试', () => {{")
            lines.append(f"    // 组件有 {cond_renders} 处条件渲染")
            lines.append(f"    it('条件为 true 时应渲染对应内容', () => {{")
            lines.append(f"      render(<{comp_name} {{{props[0] if props else 'prop'}=true}} />);")
            lines.append(f"      // TODO: 验证条件为 true 时的渲染内容")
            lines.append(f"    }});")
            lines.append("")
            lines.append(f"    it('条件为 false 时应渲染替代内容或隐藏', () => {{")
            lines.append(f"      render(<{comp_name} {{{props[0] if props else 'prop'}=false}} />);")
            lines.append(f"      // TODO: 验证条件为 false 时的渲染内容")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

        # === 列表渲染测试 ===
        if list_renders > 0:
            lines.append(f"  describe('列表渲染测试', () => {{")
            lines.append(f"    it('空列表应显示空状态', () => {{")
            list_prop = ""
            for p in props:
                if any(kw in p.lower() for kw in ["list", "items", "data", "rows", "options"]):
                    list_prop = p
                    break
            if list_prop:
                lines.append(f"      render(<{comp_name} {{{list_prop}=[]}} />);")
            else:
                lines.append(f"      render(<{comp_name} />);")
            lines.append(f"      // TODO: 验证空列表状态（如 '暂无数据' 提示）")
            lines.append(f"    }});")
            lines.append("")
            lines.append(f"    it('有数据时应正确渲染列表项', () => {{")
            if list_prop:
                lines.append(f"      const mockData = [{{ id: 1, name: '项目1' }}, {{ id: 2, name: '项目2' }}];")
                lines.append(f"      render(<{comp_name} {{{list_prop}={{mockData}}}} />);")
            else:
                lines.append(f"      render(<{comp_name} />);")
            lines.append(f"      // TODO: 验证列表项数量和内容")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

        # === 快照测试 ===
        lines.append(f"  describe('快照测试', () => {{")
        lines.append(f"    it('应与快照匹配', () => {{")
        lines.append(f"      const {{ container }} = render(<{comp_name} />);")
        lines.append(f"      expect(container).toMatchSnapshot();")
        lines.append(f"    }});")
        lines.append(f"  }});")
        lines.append("")

        # === 可访问性测试 ===
        lines.append(f"  describe('可访问性测试', () => {{")
        lines.append(f"    it('关键交互元素应有语义化标签', () => {{")
        lines.append(f"      render(<{comp_name} />);")
        lines.append(f"      // TODO: 验证按钮使用 <button> 而非 <div>")
        lines.append(f"      // expect(screen.getByRole('button')).toBeInTheDocument();")
        lines.append(f"    }});")
        lines.append(f"  }});")
        lines.append("")

        lines.append("});")
        lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成: {test_file}")


def generate_vue_tests(components: list, output_dir: str, project_path: str = ""):
    """
    生成 Vue 组件测试代码（Vitest + Vue Test Utils）

    Args:
        components: 组件列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    for comp in components:
        file_path = comp["file"]
        comp_name = comp["name"]
        props = comp.get("props", [])
        events = comp.get("events", [])
        slots = comp.get("slots", [])
        state_hooks = comp.get("state_hooks", 0)
        effect_hooks = comp.get("effect_hooks", 0)
        cond_renders = comp.get("conditional_renders", 0)
        list_renders = comp.get("list_renders", 0)

        # 生成测试文件路径
        test_file = Path(output_dir) / file_path.replace(".vue", ".test.ts")
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 计算导入路径
        import_path = file_path.replace(".vue", "")
        depth = file_path.count("/") - 1
        prefix = "../" * (depth + 1) if depth >= 0 else "./"

        lines = []
        lines.append(f"// 自动生成的组件测试 - {comp_name}")
        lines.append(f"// 测试框架: Vitest + Vue Test Utils")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据组件源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"import {{ describe, it, expect }} from 'vitest';")
        lines.append(f"import {{ mount, shallowMount }} from '@vue/test-utils';")
        lines.append(f"import {comp_name} from '{prefix}{import_path}.vue';")
        lines.append("")

        # Mock 说明
        if effect_hooks > 0:
            lines.append(f"// 组件使用了 {effect_hooks} 个 watch/effect，可能需要 Mock：")
            lines.append(f"// - Pinia: vi.mock('@/stores/xxx', () => ({{ useXxxStore: () => ({{ ... }}) }}))")
            lines.append(f"// - Router: vi.mock('vue-router', () => ({{ useRouter: () => ({{ push: vi.fn() }}) }}))")
            lines.append("")

        lines.append(f"describe('{comp_name}', () => {{")
        lines.append(f"  // 组件位置: {file_path}")
        if props:
            lines.append(f"  // Props: {', '.join(props)}")
        if events:
            lines.append(f"  // Events: {', '.join(events)}")
        if slots:
            lines.append(f"  // Slots: {', '.join(slots)}")
        if state_hooks:
            lines.append(f"  // 响应式状态: {state_hooks} 个 ref/reactive/computed")
        if cond_renders:
            lines.append(f"  // 条件渲染 (v-if): {cond_renders} 处")
        if list_renders:
            lines.append(f"  // 列表渲染 (v-for): {list_renders} 处")
        lines.append("")

        # === 渲染测试 ===
        lines.append(f"  describe('渲染测试', () => {{")
        lines.append(f"    it('使用默认 Props 应正确渲染', () => {{")
        lines.append(f"      const wrapper = mount({comp_name});")
        lines.append(f"      // TODO: 验证组件渲染了关键内容")
        lines.append(f"      // expect(wrapper.text()).toContain('...');")
        lines.append(f"    }});")
        lines.append("")

        if props:
            lines.append(f"    it('传入所有 Props 应正确渲染', () => {{")
            props_obj = ", ".join([f"{p}: '{p}_value'" for p in props[:5]])
            lines.append(f"      const wrapper = mount({comp_name}, {{")
            lines.append(f"        props: {{ {props_obj} }},")
            lines.append(f"      }});")
            for p in props[:3]:
                lines.append(f"      expect(wrapper.text()).toContain('{p}_value');")
            lines.append(f"    }});")
            lines.append("")
        lines.append(f"  }});")
        lines.append("")

        # === 事件测试 ===
        if events:
            lines.append(f"  describe('事件测试', () => {{")
            for event in events[:3]:
                lines.append(f"    it('触发 {event} 事件', async () => {{")
                lines.append(f"      const wrapper = mount({comp_name});")
                lines.append(f"      // TODO: 找到触发 {event} 的元素")
                lines.append(f"      // await wrapper.find('[data-testid=\"...\"]').trigger('click');")
                lines.append(f"      expect(wrapper.emitted('{event}')).toBeTruthy();")
                lines.append(f"    }});")
                lines.append("")
            lines.append(f"  }});")
            lines.append("")

        # === 插槽测试 ===
        if slots:
            lines.append(f"  describe('插槽测试', () => {{")
            if "default" in slots:
                lines.append(f"    it('应渲染默认插槽内容', () => {{")
                lines.append(f"      const wrapper = mount({comp_name}, {{")
                lines.append(f"        slots: {{ default: '<span class=\"custom\">自定义内容</span>' }},")
                lines.append(f"      }});")
                lines.append(f"      expect(wrapper.find('.custom').exists()).toBe(true);")
                lines.append(f"    }});")
                lines.append("")
            for slot in slots:
                if slot != "default":
                    lines.append(f"    it('应渲染 {slot} 插槽内容', () => {{")
                    lines.append(f"      const wrapper = mount({comp_name}, {{")
                    lines.append(f"        slots: {{ {slot}: '<span class=\"{slot}-content\">{slot} 内容</span>' }},")
                    lines.append(f"      }});")
                    lines.append(f"      expect(wrapper.find('.{slot}-content').exists()).toBe(true);")
                    lines.append(f"    }});")
                    lines.append("")
            lines.append(f"  }});")
            lines.append("")

        # === 条件渲染测试 ===
        if cond_renders > 0:
            lines.append(f"  describe('条件渲染测试', () => {{")
            lines.append(f"    // 组件有 {cond_renders} 处 v-if 条件渲染")
            lines.append(f"    it('条件为 true 时应渲染对应内容', () => {{")
            cond_prop = props[0] if props else "prop"
            lines.append(f"      const wrapper = mount({comp_name}, {{ props: {{ {cond_prop}: true }} }});")
            lines.append(f"      // TODO: 验证条件为 true 时的渲染内容")
            lines.append(f"    }});")
            lines.append("")
            lines.append(f"    it('条件为 false 时应隐藏或显示替代内容', () => {{")
            lines.append(f"      const wrapper = mount({comp_name}, {{ props: {{ {cond_prop}: false }} }});")
            lines.append(f"      // TODO: 验证条件为 false 时的渲染内容")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

        # === 列表渲染测试 ===
        if list_renders > 0:
            lines.append(f"  describe('列表渲染测试', () => {{")
            lines.append(f"    it('空列表应显示空状态', () => {{")
            list_prop = ""
            for p in props:
                if any(kw in p.lower() for kw in ["list", "items", "data", "rows", "options"]):
                    list_prop = p
                    break
            if list_prop:
                lines.append(f"      const wrapper = mount({comp_name}, {{ props: {{ {list_prop}: [] }} }});")
            else:
                lines.append(f"      const wrapper = mount({comp_name});")
            lines.append(f"      // TODO: 验证空列表状态")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

        lines.append("});")
        lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成: {test_file}")


def generate_angular_tests(components: list, output_dir: str, project_path: str = ""):
    """
    生成 Angular 组件测试代码（Jest + Angular Testing Library）

    Args:
        components: 组件列表
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    for comp in components:
        file_path = comp["file"]
        comp_name = comp["name"]
        props = comp.get("props", [])
        events = comp.get("events", [])

        test_file = Path(output_dir) / file_path.replace(".component.ts", ".component.spec.ts")
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 提取包名
        package = ""
        if "src/app/" in file_path:
            rel = file_path.replace("src/app/", "").replace(".component.ts", "")
            parts = rel.split("/")
            if len(parts) > 1:
                package = ".".join(parts[:-1])

        lines = []
        lines.append(f"// 自动生成的组件测试 - {comp_name}")
        lines.append(f"// 测试框架: Jest + Angular Testing Library")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据组件源码分析结果填充具体测试值和断言")
        lines.append("")
        if package:
            lines.append(f"import {{ ComponentFixture }} from '@angular/core/testing';")
        lines.append(f"import {{ render, screen }} from '@testing-library/angular';")
        lines.append(f"import {comp_name} from './{comp_name}.component';")
        lines.append("")

        lines.append(f"describe('{comp_name}', () => {{")
        lines.append(f"  // 组件位置: {file_path}")
        if props:
            lines.append(f"  // @Input: {', '.join(props)}")
        if events:
            lines.append(f"  // @Output: {', '.join(events)}")
        lines.append("")

        lines.append(f"  it('应正确创建组件', async () => {{")
        lines.append(f"    await render({comp_name});")
        lines.append(f"    // TODO: 验证组件渲染了关键内容")
        lines.append(f"  }});")
        lines.append("")

        if props:
            lines.append(f"  it('传入 @Input 应正确渲染', async () => {{")
            props_obj = ", ".join([f"{p}: '{p}_value'" for p in props[:5]])
            lines.append(f"    await render({comp_name}, {{")
            lines.append(f"      componentInputs: {{ {props_obj} }},")
            lines.append(f"    }});")
            lines.append(f"    // TODO: 验证渲染内容")
            lines.append(f"  }});")
            lines.append("")

        if events:
            for event in events[:3]:
                lines.append(f"  it('@Output {event} 应在交互时触发', async () => {{")
                lines.append(f"    // TODO: 设置事件监听并触发交互")
                lines.append(f"  }});")
                lines.append("")

        lines.append("});")
        lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成: {test_file}")


def generate_component_tests(scan_result_path: str, output_dir: str, project_path: str = ""):
    """
    根据扫描结果生成对应框架的组件测试代码

    Args:
        scan_result_path: 扫描结果 JSON 文件路径
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 使用公共模块安全读取 JSON
    data = load_json(scan_result_path)
    if data is None:
        print(f"错误：无法读取扫描结果文件 - {scan_result_path}")
        return

    components = data.get("components", [])
    if not components:
        print("没有可测试的组件")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    framework = data.get("framework", "unknown")
    print(f"\n生成 {framework} 组件测试代码...")

    if framework in ("react", "nextjs"):
        generate_react_tests(components, output_dir, project_path)
    elif framework in ("vue", "nuxtjs"):
        generate_vue_tests(components, output_dir, project_path)
    elif framework == "angular":
        generate_angular_tests(components, output_dir, project_path)
    else:
        print(f"暂不支持 {framework} 框架的组件测试代码生成")
        return

    print(f"\n测试文件已生成到: {output_dir}")
    print(f"共生成 {len(components)} 个组件的测试用例")
    print(f"\n注意：生成的测试代码为骨架，包含 TODO 占位符")
    print(f"   AI 需要读取组件源码分析结果，填充具体的测试值和断言")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_component_tests.py <扫描结果JSON> <输出目录> [项目路径]")
        print("示例: python generate_component_tests.py scan_result.json ./tests/ /path/to/project")
        sys.exit(1)

    project = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_component_tests(sys.argv[1], sys.argv[2], project)
