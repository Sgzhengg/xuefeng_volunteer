from typing import List, Dict, Any, Optional


class VolunteerSimulatorService:
    """志愿模拟器服务 - 生成冲稳保垫方案"""

    def __init__(self):
        pass

    async def generate_volunteer_scheme(
        self,
        province: str,
        score: int,
        subject_type: str,
        target_majors: List[str],
        rank: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成冲稳保垫志愿方案

        Args:
            province: 省份
            score: 分数
            subject_type: 科类
            target_majors: 目标专业列表
            rank: 位次（可选）
            preferences: 偏好设置（城市、院校层次等）

        Returns:
            志愿方案，包含冲、稳、保、垫四类院校
        """

        scheme = {
            "province": province,
            "score": score,
            "subject_type": subject_type,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "冲刺": [],
            "稳妥": [],
            "保底": [],
            "垫底": [],
        }

        # 根据分数段确定院校范围
        score_range = self._calculate_score_range(score)

        # 为每个目标专业生成方案
        for major in target_majors:
            # 生成冲刺院校（分数高于用户10-20分）
            chong_universities = await self._generate_chong_universities(
                province, score, subject_type, major, score_range
            )
            scheme["冲刺"].extend(chong_universities)

            # 生成稳妥院校（分数接近用户±10分）
            wen_universities = await self._generate_wen_universities(
                province, score, subject_type, major, score_range
            )
            scheme["稳妥"].extend(wen_universities)

            # 生成保底院校（分数低于用户20-30分）
            bao_universities = await self._generate_bao_universities(
                province, score, subject_type, major, score_range
            )
            scheme["保底"].extend(bao_universities)

            # 生成垫底院校（分数低于用户40+分）
            dian_universities = await self._generate_dian_universities(
                province, score, subject_type, major, score_range
            )
            scheme["垫底"].extend(dian_universities)

        # 去重和排序
        scheme = self._deduplicate_and_sort(scheme)

        # 生成建议说明
        scheme["建议说明"] = self._generate_scheme_advice(scheme)

        return {
            "success": True,
            "data": scheme,
        }

    def _calculate_score_range(self, score: int) -> Dict[str, int]:
        """计算分数段"""
        return {
            "chong_high": score + 30,
            "chong_low": score + 10,
            "wen_high": score + 10,
            "wen_low": score - 10,
            "bao_high": score - 10,
            "bao_low": score - 30,
            "dian_high": score - 30,
            "dian_low": score - 50,
        }

    async def _generate_chong_universities(
        self,
        province: str,
        score: int,
        subject_type: str,
        major: str,
        score_range: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """生成冲刺院校"""
        # 这里应该调用真实的院校查询API
        # 暂时返回模拟数据
        return [
            {
                "院校名称": "浙江大学",
                "专业": major,
                "预估概率": "30-40%",
                "建议": "冲刺，有希望但风险较大",
                "类型": "985",
            },
            {
                "院校名称": "上海交通大学",
                "专业": major,
                "预估概率": "25-35%",
                "建议": "冲刺，需要运气",
                "类型": "985",
            },
        ]

    async def _generate_wen_universities(
        self,
        province: str,
        score: int,
        subject_type: str,
        major: str,
        score_range: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """生成稳妥院校"""
        return [
            {
                "院校名称": "南京大学",
                "专业": major,
                "预估概率": "60-70%",
                "建议": "稳妥，录取概率较大",
                "类型": "985",
            },
            {
                "院校名称": "同济大学",
                "专业": major,
                "预估概率": "65-75%",
                "建议": "稳妥，性价比高",
                "类型": "985",
            },
        ]

    async def _generate_bao_universities(
        self,
        province: str,
        score: int,
        subject_type: str,
        major: str,
        score_range: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """生成保底院校"""
        return [
            {
                "院校名称": "苏州大学",
                "专业": major,
                "预估概率": "85-95%",
                "建议": "保底，基本没问题",
                "类型": "211",
            },
            {
                "院校名称": "南京理工大学",
                "专业": major,
                "预估概率": "80-90%",
                "建议": "保底，工科强校",
                "type": "211",
            },
        ]

    async def _generate_dian_universities(
        self,
        province: str,
        score: int,
        subject_type: str,
        major: str,
        score_range: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """生成垫底院校"""
        return [
            {
                "院校名称": "江南大学",
                "专业": major,
                "预估概率": "95%+",
                "建议": "垫底，肯定能上",
                "type": "211",
            }
        ]

    def _deduplicate_and_sort(self, scheme: Dict[str, Any]) -> Dict[str, Any]:
        """去重和排序"""
        # 简单去重（按院校名称+专业）
        seen = set()
        for category in ["冲刺", "稳妥", "保底", "垫底"]:
            unique_items = []
            for item in scheme[category]:
                key = f"{item.get('院校名称', '')}-{item.get('专业', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)
            scheme[category] = unique_items

        return scheme

    def _generate_scheme_advice(self, scheme: Dict[str, Any]) -> List[str]:
        """生成方案建议"""
        advice = []

        # 统计各类别数量
        chong_count = len(scheme["冲刺"])
        wen_count = len(scheme["稳妥"])
        bao_count = len(scheme["保底"])
        dian_count = len(scheme["垫底"])

        if chong_count > 0:
            advice.append(f"有{chong_count}个冲刺院校，建议最多选1-2个")

        if wen_count > 0:
            advice.append(f"有{wen_count}个稳妥院校，这是重点，建议选3-4个")

        if bao_count > 0:
            advice.append(f"有{bao_count}个保底院校，建议选2-3个")

        if dian_count > 0:
            advice.append(f"有{dian_count}个垫底院校，建议选1个即可")

        advice.append("冲稳保垫比例建议：冲刺20%，稳妥40%，保底30%，垫底10%")

        return advice


# 导入 datetime
from datetime import datetime

# 全局实例
volunteer_simulator_service = VolunteerSimulatorService()
