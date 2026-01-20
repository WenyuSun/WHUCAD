# WHUCAD Vector Format Explanation / WHUCAD 向量格式说明

[English](#english-version) | [中文](#中文版本)

---

## 中文版本

### WHUCAD CAD零件向量（vec）格式详细说明

本文档详细解释了WHUCAD数据集中CAD零件向量表示的每个位置的含义。

#### 1. 向量总体结构

每个CAD模型都被表示为一个序列的向量，形状为 `(seq_len, 1 + N_ARGS)`，其中：
- `seq_len`: 序列长度（最大为 MAX_TOTAL_LEN = 100）
- 第一列（索引0）: **命令类型** (command)
- 后续列（索引1-32）: **命令参数** (arguments)，总共 N_ARGS = 32 个参数

因此，每个向量的总长度为 1 + 32 = 33。

#### 2. 参数分组结构

32个参数被分为4组：

```python
N_ARGS = 32 = N_ARGS_SKETCH + N_ARGS_EXT + N_ARGS_FINISH_PARAM + N_ARGS_SELECT_PARAM
```

详细分解：
- **N_ARGS_SKETCH = 5**: 草图参数（位置 1-5）
- **N_ARGS_EXT = 14**: 拉伸/旋转操作参数（位置 6-19）
  - N_ARGS_PLANE = 3: 草图平面方向（位置 6-8）
  - N_ARGS_TRANS = 4: 草图平面原点 + 边界框尺寸（位置 9-12）
  - N_ARGS_BODY_PARAM = 7: 实体操作参数（位置 13-19）
- **N_ARGS_FINISH_PARAM = 9**: 精修特征参数（位置 20-28）
- **N_ARGS_SELECT_PARAM = 4**: 选择参数（位置 29-32）

#### 3. 向量位置详细说明

每个向量包含33个值，具体含义如下：

| 位置索引 | 参数分组 | 参数名称 | 描述 |
|---------|---------|---------|------|
| **0** | 命令 | command | 命令类型索引（见下文命令列表） |
| **1** | SKETCH | x | 草图曲线端点 x 坐标 |
| **2** | SKETCH | y | 草图曲线端点 y 坐标 |
| **3** | SKETCH | alpha | 圆弧/圆的角度参数 |
| **4** | SKETCH | f | 圆弧/圆的额外角度参数 |
| **5** | SKETCH | r | 圆/圆弧的半径 |
| **6** | PLANE | theta | 草图平面方向角θ（俯仰角） |
| **7** | PLANE | phi | 草图平面方向角φ（偏航角） |
| **8** | PLANE | gamma | 草图平面方向角γ（横滚角） |
| **9** | TRANS | p_x | 草图平面原点 x 坐标 |
| **10** | TRANS | p_y | 草图平面原点 y 坐标 |
| **11** | TRANS | p_z | 草图平面原点 z 坐标 |
| **12** | TRANS | s | 草图边界框尺寸 |
| **13** | BODY_PARAM | length1 | 拉伸/凹槽长度1 |
| **14** | BODY_PARAM | length2 | 拉伸/凹槽长度2 |
| **15** | BODY_PARAM | length1_type | 长度1的类型 |
| **16** | BODY_PARAM | length2_type | 长度2的类型 |
| **17** | BODY_PARAM | angle1 | 旋转角度1 |
| **18** | BODY_PARAM | angle2 | 旋转角度2 |
| **19** | BODY_PARAM | boolean | 布尔操作类型 |
| **20** | FINISH_PARAM | thickness1 | 壳体/倒角厚度1 |
| **21** | FINISH_PARAM | thickness2 | 壳体第二厚度 |
| **22** | FINISH_PARAM | length1 | 倒角长度1 |
| **23** | FINISH_PARAM | length2 | 倒角长度2/角度 |
| **24** | FINISH_PARAM | radius | 圆角半径 |
| **25** | FINISH_PARAM | alpha | 拔模角度 |
| **26** | FINISH_PARAM | hole_r | 孔的半径 |
| **27** | FINISH_PARAM | hole_depth | 孔的深度 |
| **28** | FINISH_PARAM | hole_type | 孔的类型 |
| **29** | SELECT_PARAM | select_type | 选择类型（Wire/Face/Edge等） |
| **30** | SELECT_PARAM | body_type | 实体类型 |
| **31** | SELECT_PARAM | body_no | 实体编号 |
| **32** | SELECT_PARAM | no | 选择编号 |

**注意**：实际向量索引从0开始，因此参数从索引1开始到索引32结束（共32个参数）。

#### 4. 命令类型列表

共有27种命令类型（索引从0到26，共27个）：

##### 草图命令（Sketch Commands, 0-4）
- **0: Line** - 直线
  - 使用参数：x(1), y(2)
- **1: Arc** - 圆弧
  - 使用参数：x(1), y(2), alpha(3), f(4)
- **2: Circle** - 圆
  - 使用参数：x(1), y(2), r(5)
- **3: Spline** - 样条曲线
  - 使用参数：无（需要配合SCP使用）
- **4: SCP** - 样条控制点
  - 使用参数：x(1), y(2)

##### 控制命令（Control Commands, 5-6）
- **5: EOS** - 草图结束标记
- **6: SOL** - 实体开始标记

##### 3D操作命令（3D Operation Commands, 7-10）
- **7: Ext** - 拉伸
  - 使用参数：平面参数(6-12), length1(13), length2(14), length1_type(15), length2_type(16), boolean(19)
- **8: Rev** - 旋转
  - 使用参数：平面参数(6-12), angle1(17), angle2(18), boolean(19)
- **9: Pocket** - 凹槽
  - 使用参数：平面参数(6-12), length1(13), length2(14), length1_type(15), length2_type(16)
- **10: Groove** - 旋转凹槽
  - 使用参数：平面参数(6-12), angle1(17), angle2(18)

##### 精修特征命令（Finishing Feature Commands, 11-16）
- **11: Shell** - 壳体
  - 使用参数：thickness1(20), thickness2(21)
- **12: Chamfer** - 倒角
  - 使用参数：length1(22), length2(23)
- **13: Fillet** - 圆角
  - 使用参数：radius(24)
- **14: Draft** - 拔模
  - 使用参数：alpha(25)
- **15: Mirror** - 镜像
  - 使用参数：无
- **16: Hole** - 孔
  - 使用参数：x(1), y(2), 平面参数(6-11) [6个坐标系参数], hole_r(26), hole_depth(27), hole_type(28)

##### 辅助命令（Auxiliary Commands, 17-26）
- **17: Topo** - 拓扑标记
- **18: Select** - 选择操作
  - 使用参数：select_type(29), body_type(30), body_no(31), no(32)
- **19: MirrorStart** - 镜像开始标记
- **20: NoSharedIncluded** - 无共享包含标记
- **21: NoSharedIncludedEnd** - 无共享包含结束标记
- **22: AllOrientedIncluded1** - 全部定向包含标记1
- **23: AllOrientedIncluded2** - 全部定向包含标记2
- **24: AllOrientedIncludedEnd** - 全部定向包含结束标记
- **25: AllPartiallySharedIncluded** - 全部部分共享包含标记
- **26: AllPartiallySharedIncludedEnd** - 全部部分共享包含结束标记

#### 5. 数据格式说明

- **数值范围**：所有参数都被量化为整数，范围通常是 0-255（ARGS_DIM = 256）
- **填充值**：未使用的参数位置填充为 -1（PAD_VAL = -1）
- **归一化**：坐标和尺寸参数经过归一化处理，归一化因子为 NORM_FACTOR = 0.75

#### 6. CAD序列示例

一个典型的CAD模型序列可能如下：

```
1. SOL (6) - 实体开始
2. Line (0, x1, y1, ...) - 绘制直线到(x1,y1)
3. Arc (1, x2, y2, alpha, f, ...) - 绘制圆弧到(x2,y2)
4. Line (0, x3, y3, ...) - 绘制直线到(x3,y3)
5. EOS (5) - 草图结束
6. Ext (7, ..., theta, phi, gamma, px, py, pz, s, len1, len2, ..., bool) - 拉伸操作
7. Select (18, ..., select_type, body_type, body_no, no) - 选择面/边
8. Fillet (13, ..., radius, ...) - 圆角
9. EOS (5) - 序列结束
```

#### 7. 数据存储

- 格式：HDF5 (.h5)
- 数据集名称：`"vec"`
- 形状：`(seq_len, 1 + N_ARGS)` = `(seq_len, 33)`
- 数据类型：整数（int）

---

## English Version

### WHUCAD CAD Part Vector (vec) Format Detailed Explanation

This document provides a detailed explanation of the meaning of each position in the CAD part vector representation used in the WHUCAD dataset.

#### 1. Overall Vector Structure

Each CAD model is represented as a sequence of vectors with shape `(seq_len, 1 + N_ARGS)`, where:
- `seq_len`: Sequence length (maximum MAX_TOTAL_LEN = 100)
- First column (index 0): **Command type**
- Subsequent columns (indices 1-32): **Command arguments**, total N_ARGS = 32 parameters

Therefore, each vector has a total length of 1 + 32 = 33.

#### 2. Parameter Group Structure

The 32 parameters are divided into 4 groups:

```python
N_ARGS = 32 = N_ARGS_SKETCH + N_ARGS_EXT + N_ARGS_FINISH_PARAM + N_ARGS_SELECT_PARAM
```

Breakdown:
- **N_ARGS_SKETCH = 5**: Sketch parameters (positions 1-5)
- **N_ARGS_EXT = 14**: Extrusion/revolution operation parameters (positions 6-19)
  - N_ARGS_PLANE = 3: Sketch plane orientation (positions 6-8)
  - N_ARGS_TRANS = 4: Sketch plane origin + bounding box size (positions 9-12)
  - N_ARGS_BODY_PARAM = 7: Body operation parameters (positions 13-19)
- **N_ARGS_FINISH_PARAM = 9**: Finishing feature parameters (positions 20-28)
- **N_ARGS_SELECT_PARAM = 4**: Selection parameters (positions 29-32)

#### 3. Detailed Vector Position Explanation

Each vector contains 33 values with the following meanings:

| Index | Parameter Group | Parameter Name | Description |
|-------|----------------|----------------|-------------|
| **0** | Command | command | Command type index (see command list below) |
| **1** | SKETCH | x | Sketch curve endpoint x-coordinate |
| **2** | SKETCH | y | Sketch curve endpoint y-coordinate |
| **3** | SKETCH | alpha | Angle parameter for arc/circle |
| **4** | SKETCH | f | Additional angle parameter for arc/circle |
| **5** | SKETCH | r | Radius for circle/arc |
| **6** | PLANE | theta | Sketch plane orientation angle θ (pitch) |
| **7** | PLANE | phi | Sketch plane orientation angle φ (yaw) |
| **8** | PLANE | gamma | Sketch plane orientation angle γ (roll) |
| **9** | TRANS | p_x | Sketch plane origin x-coordinate |
| **10** | TRANS | p_y | Sketch plane origin y-coordinate |
| **11** | TRANS | p_z | Sketch plane origin z-coordinate |
| **12** | TRANS | s | Sketch bounding box size |
| **13** | BODY_PARAM | length1 | Extrusion/pocket length 1 |
| **14** | BODY_PARAM | length2 | Extrusion/pocket length 2 |
| **15** | BODY_PARAM | length1_type | Type of length 1 |
| **16** | BODY_PARAM | length2_type | Type of length 2 |
| **17** | BODY_PARAM | angle1 | Revolution angle 1 |
| **18** | BODY_PARAM | angle2 | Revolution angle 2 |
| **19** | BODY_PARAM | boolean | Boolean operation type |
| **20** | FINISH_PARAM | thickness1 | Shell/chamfer thickness 1 |
| **21** | FINISH_PARAM | thickness2 | Shell second thickness |
| **22** | FINISH_PARAM | length1 | Chamfer length 1 |
| **23** | FINISH_PARAM | length2 | Chamfer length 2/angle |
| **24** | FINISH_PARAM | radius | Fillet radius |
| **25** | FINISH_PARAM | alpha | Draft angle |
| **26** | FINISH_PARAM | hole_r | Hole radius |
| **27** | FINISH_PARAM | hole_depth | Hole depth |
| **28** | FINISH_PARAM | hole_type | Hole type |
| **29** | SELECT_PARAM | select_type | Selection type (Wire/Face/Edge, etc.) |
| **30** | SELECT_PARAM | body_type | Body type |
| **31** | SELECT_PARAM | body_no | Body number |
| **32** | SELECT_PARAM | no | Selection number |

**Note**: Actual vector indices start from 0, so parameters range from index 1 to index 32 (32 parameters total).

#### 4. Command Type List

There are 27 command types in total (indices from 0 to 26, total of 27 commands):

##### Sketch Commands (0-4)
- **0: Line** - Straight line
  - Uses parameters: x(1), y(2)
- **1: Arc** - Arc
  - Uses parameters: x(1), y(2), alpha(3), f(4)
- **2: Circle** - Circle
  - Uses parameters: x(1), y(2), r(5)
- **3: Spline** - Spline curve
  - Uses parameters: None (requires SCP)
- **4: SCP** - Spline Control Point
  - Uses parameters: x(1), y(2)

##### Control Commands (5-6)
- **5: EOS** - End of Sketch marker
- **6: SOL** - Start of Solid marker

##### 3D Operation Commands (7-10)
- **7: Ext** - Extrusion
  - Uses parameters: plane params(6-12), length1(13), length2(14), length1_type(15), length2_type(16), boolean(19)
- **8: Rev** - Revolution
  - Uses parameters: plane params(6-12), angle1(17), angle2(18), boolean(19)
- **9: Pocket** - Pocket
  - Uses parameters: plane params(6-12), length1(13), length2(14), length1_type(15), length2_type(16)
- **10: Groove** - Groove (revolution pocket)
  - Uses parameters: plane params(6-12), angle1(17), angle2(18)

##### Finishing Feature Commands (11-16)
- **11: Shell** - Shell
  - Uses parameters: thickness1(20), thickness2(21)
- **12: Chamfer** - Chamfer
  - Uses parameters: length1(22), length2(23)
- **13: Fillet** - Fillet
  - Uses parameters: radius(24)
- **14: Draft** - Draft
  - Uses parameters: alpha(25)
- **15: Mirror** - Mirror
  - Uses parameters: None
- **16: Hole** - Hole
  - Uses parameters: x(1), y(2), plane params(6-11) [6 coordinate system parameters], hole_r(26), hole_depth(27), hole_type(28)

##### Auxiliary Commands (17-26)
- **17: Topo** - Topology marker
- **18: Select** - Selection operation
  - Uses parameters: select_type(29), body_type(30), body_no(31), no(32)
- **19: MirrorStart** - Mirror start marker
- **20: NoSharedIncluded** - No shared included marker
- **21: NoSharedIncludedEnd** - No shared included end marker
- **22: AllOrientedIncluded1** - All oriented included marker 1
- **23: AllOrientedIncluded2** - All oriented included marker 2
- **24: AllOrientedIncludedEnd** - All oriented included end marker
- **25: AllPartiallySharedIncluded** - All partially shared included marker
- **26: AllPartiallySharedIncludedEnd** - All partially shared included end marker

#### 5. Data Format Details

- **Value range**: All parameters are quantized to integers, typically 0-255 (ARGS_DIM = 256)
- **Padding value**: Unused parameter positions are filled with -1 (PAD_VAL = -1)
- **Normalization**: Coordinate and dimension parameters are normalized with NORM_FACTOR = 0.75

#### 6. CAD Sequence Example

A typical CAD model sequence might look like:

```
1. SOL (6) - Start of solid
2. Line (0, x1, y1, ...) - Draw line to (x1,y1)
3. Arc (1, x2, y2, alpha, f, ...) - Draw arc to (x2,y2)
4. Line (0, x3, y3, ...) - Draw line to (x3,y3)
5. EOS (5) - End of sketch
6. Ext (7, ..., theta, phi, gamma, px, py, pz, s, len1, len2, ..., bool) - Extrusion
7. Select (18, ..., select_type, body_type, body_no, no) - Select face/edge
8. Fillet (13, ..., radius, ...) - Fillet
9. EOS (5) - End of sequence
```

#### 7. Data Storage

- Format: HDF5 (.h5)
- Dataset name: `"vec"`
- Shape: `(seq_len, 1 + N_ARGS)` = `(seq_len, 33)`
- Data type: Integer (int)

---

## References / 参考资料

For more details, please refer to:
- Main code: `/cadlib/macro.py`
- Dataset implementation: `/dataset/cad_dataset.py`
- CAD class definitions: `/cadlib/CAD_Class.py`

更多详细信息，请参考：
- 主要代码：`/cadlib/macro.py`
- 数据集实现：`/dataset/cad_dataset.py`
- CAD类定义：`/cadlib/CAD_Class.py`
